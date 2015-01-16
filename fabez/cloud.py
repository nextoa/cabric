# -*- coding: utf-8 -*-


from fabez.env import *

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

try:
    import qingcloud.iaas  # used for ide autocomplete
except:

    pass

from fabez.lib import _detected_ssh_public_key_type


def cloud_run(func, hold_func=None, strict=True, return_key=None, func_args=[], func_kwargs={}):
    """
    execute cloud operation
    :return:
    """

    result = func(*func_args, **func_kwargs)

    print("[Execute]:{}".format(func.__name__))

    if not result:
        raise Exception("Network error")

    if result['ret_code']:
        if strict:
            raise Exception(result['message'])
        else:
            print("[Warning]:{}".format(result['message']))

    data = None
    if return_key:
        data = result[return_key]

    if not strict and result['ret_code']:
        return data

    if hold_func is False:
        current_hold_func = False
    else:
        current_hold_func = hold_func if hold_func else ez_env.cloud_processor

    if not current_hold_func:
        return data

    job_id = result['job_id']
    stop = False
    counter = 0
    print("[Holding]: {} ...".format(job_id))

    while True:
        result = current_hold_func([job_id])

        for v in result['job_set']:
            if v['status'] in ['successful']:
                stop = True
            elif v['status'] in ['pending', 'working']:

                time.sleep(1)
            else:
                raise Exception(v)
            pass

            counter += 1
            print("." * counter)

        if stop:
            break
        pass

    return data


def cloud_update(buff, file='./config/cabric/cloud.yaml'):
    return dump(buff, open(file, 'w'), Dumper=Dumper)


def cloud_read(file='./config/cabric/cloud.yaml'):
    return load(open(file, 'r'), Loader=Loader)


def cloud_connect(handler=None):
    handler = handler if handler else ez_env.cloud_handler

    h = handler.connect_to_zone(*ez_env.cloud)
    ez_env.cloud_processor = h.describe_jobs
    ez_env.cloud_active = h
    return h


def cloud_init(handler=None):
    if ez_env.cloud_active:
        return ez_env.cloud_active

    return cloud_connect(handler)


# ########### instance #################


def cc_show_instance_list(search_word=None, tag='all'):
    """
    :return: [instance_id, eip_id, eip_addr, vxnet, status_time, instance_type]
    """

    h = cloud_init()
    result = h.describe_instances()

    data = []

    d = result.get('instance_set')

    filters = ['running', 'stopped']

    if tag == 'start':
        filters = ['running']
    elif tag == 'stop':
        filters = ['stopped']

    for v in d:
        if v.get('status') in filters:
            data.append(v)
            pass

    if search_word:
        filter_data = []
        names = [v['instance_name'] for v in data]
        l = len(search_word)

        for k,v in enumerate(names):
            if v[0:l] == search_word:
                filter_data.append(data[k])
                pass
            pass

        data = filter_data
        pass

    return data


def cc_show_instance(instance_id):
    data = cc_show_instance_list()
    instances = [v['instance_id'] for v in data]

    try:
        pos = instances.index(instance_id)
    except:
        pos = -1
        pass

    if pos > -1:
        return data[pos]

    pass


def cc_create_instance(group, owner='root', part_time=False, image_id='centos65x64d', cpu=1, memory=1024):
    """
    @todo support user image_id
    :return:
    """
    h = cloud_init()

    exist_instances = cc_show_instance_list(group)

    if not exist_instances:
        name = group + '01'
    else:
        exist_names = [v['instance_name'] for v in exist_instances]
        exist_names.sort()
        last_id = exist_names.pop()[len(group):]
        name = '{}{:02d}'.format(group, int(last_id) + 1)

    config = cloud_read()

    vxnet_id = config['vxnet']

    _, key_id = cc_show_pub_key(owner)

    instances = cloud_run(h.run_instances, func_kwargs=dict(image_id=image_id, cpu=cpu, memory=memory, instance_name=name, vxnets=[vxnet_id], login_mode='keypair', login_keypair=key_id),
                          return_key='instances')

    conf_part_time = config.get('part_time', {})
    group_part_time = conf_part_time.get(group, set())

    if part_time:
        group_part_time.add(instances[0])
        conf_part_time[group] = group_part_time

    config['part_time'] = conf_part_time
    cloud_update(config)

    instance_info = cc_show_instance(instances[0])
    private_ip = instance_info['vxnets'][0]['private_ip']

    while True:
        if not private_ip:
            instance_info = cc_show_instance(instances[0])
            private_ip = instance_info['vxnets'][0]['private_ip']
            print("Initial private IP...")
            time.sleep(5)
        else:
            break

    return instances[0], 'root@' + private_ip


def cc_create_rom(template_name):
    """
    @todo
    :param template_name:
    :return:
    """

    # instance_info = cc_show_instance(instances[0])

    pass




# ########### part-time ###############
def cc_start_part_time(group):

    h = cloud_init()
    config = cloud_read()
    conf_part_time = config.get('part_time')
    group_part_time = conf_part_time.get(group, set())

    if group_part_time:
        cloud_run(h.start_instances, func_args=[
            list(group_part_time)
        ])
    else:
        print("No part time instance found,skip start.")

    pass



def cc_stop_part_time(group):

    h = cloud_init()
    config = cloud_read()
    conf_part_time = config.get('part_time')
    group_part_time = conf_part_time.get(group, set())

    if group_part_time:
        cloud_run(h.stop_instances, func_args=[
            list(group_part_time)
        ])
    else:
        print("No part time instance found,skip stop.")

    pass



def cc_eips_free(wait=1, tries=100, *args, **kwargs):
    """
    @todo don't use this
    get free ip list
    :param wait:
    :param tries:
    :param args:
    :param kwargs:
    :return:
    """
    h = cloud_init()

    addrs = set()
    process = 0

    while True:
        data = h.describe_eips()

        if not data.get('eip_set'):
            print("get new ip fail,try 1s later.")
            time.sleep(1)
            continue

        for eip in data['eip_set']:
            if eip['status'] == 'available':
                addrs.add(eip['eip_id'])
                pass
            pass

        if len(addrs) >= wait:
            break

        process += 1
        if process == tries:
            break

        time.sleep(1)
        pass

    return list(addrs)




# ########### datacenter ###############
def cc_create_datacenter():
    """
    create a data-center
    :param pubkey:
    :return:
    """
    config = cloud_read()

    # create user public key
    cc_create_pub_key(config['author'])

    # create route
    lan = config['lan']
    if lan:
        vxnet_id, router_id = cc_create_lan(lan)
    else:
        vxnet_id, router_id = 'vxnet-0', None

    config = cloud_read()
    config['vxnet'] = vxnet_id
    config['router'] = router_id
    # update config
    cloud_update(config)

    if lan:
        # bind public ip
        # cc_bind_public_ip(router_id,'router')
        # open vpn set
        # cc_bind_vpn(router_id)
        # @todo: open firewall port
        # @todo: add default port forward
        # cc_create_load_balance(vxnet_id)
        pass

    pass


# ########## load balance ###################
def cc_create_load_balance(vxnet_id):
    """
    @todo don't use it
    :param vxnet_id:
    :return:
    """

    h = cloud_init()
    eip = cc_create_public_ip()[0]
    h.create_loadbalancer(eip)

    pass


# ########## fire wall ###################

def cc_reset_firewall(wall_type='datacenter'):
    pass


# ########## public ip ###################
def cc_create_public_ip():
    # allocate ip
    eips = cloud_run(h.allocate_eips, hold_func=False, return_key='eips', func_args=[
        1, 1
    ])
    return eips


def cc_bind_public_ip(device_id, device_type):
    h = cloud_init()

    eip = eips[0]
    if device_type == 'router':
        cloud_run(h.modify_router_attributes, hold_func=False, func_kwargs=dict(router=device_id, eip=eip))
    elif device_type == 'instance':
        # assign ip
        cloud_run(h.associate_eip, func_args=[eip, device_id])
    elif device_type == 'load-balance':

        pass

    pass


# ########## router ###################
def cc_bind_vpn(router_id):
    h = cloud_init()
    cloud_run(h.add_router_statics, hold_func=False, func_args=[router_id, [{'static_type': 2}]])
    cloud_run(h.update_routers, func_args=[router_id])
    pass


# ########## private lan ###################

def cc_create_lan(lan, name='default'):
    h = cloud_init()

    result = h.create_vxnets(name)

    if result['ret_code']:
        raise Exception(result)

    vxnet_id = result['vxnets'][0]

    routers = cloud_run(h.create_routers, func_kwargs=dict(router_name=name), return_key='routers')
    router_id = routers[0]

    cloud_run(h.join_router, func_kwargs=dict(vxnet=vxnet_id, router=router_id, ip_network=lan))

    return vxnet_id, router_id


# ########## public key ###################

def cc_create_pub_key(name='root', pub_key='~/.ssh/id_rsa.pub'):
    h = cloud_init()
    buff = None
    _, key_id = cc_show_pub_key(name)

    if key_id:
        raise Exception("keypair name already exists.")

    with open(os.path.expanduser(pub_key)) as fh:
        buff = fh.read()
        pass

    result = h.create_keypair(name, mode='user', public_key=buff, encrypt_method=_detected_ssh_public_key_type(pub_key))

    return True if result['ret_code'] == 0 else False


def cc_delete_pub_key(name):
    h = cloud_init()

    key_data = cc_show_pub_key(name)

    key_name, key_id = key_data

    if not key_id:
        raise Exception("ssh key not exists.")

    # detech key pair
    instances = cc_show_instance_list('all')

    h.detach_keypairs([key_id], instances)
    h.delete_keypairs([key_id])

    pass


def cc_show_pub_key_list(search_word=None):
    h = cloud_init()

    result = h.describe_key_pairs(search_word=search_word)

    names = []
    key_ids = []

    key_data = []

    if result['total_count']:
        key_data = [(v['keypair_name'], v['keypair_id']) for v in result['keypair_set']]

    return key_data


def cc_show_pub_key(name):
    keys = cc_show_pub_key_list(name)

    try:
        compare = zip(*keys)[0]
        pos = compare.index(name)
    except:
        pos = -1
        pass

    if pos > -1:
        return keys[pos]

    return None, None


