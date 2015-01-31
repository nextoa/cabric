# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from cabric.env import *

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

try:
    import qingcloud.iaas  # used for ide autocomplete
except:

    pass

from cabric.lib import _detected_ssh_public_key_type







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




# ########## public key ###################

# def cc_create_pub_key(name='root', pub_key='~/.ssh/id_rsa.pub'):
#     h = cloud_init()
#     buff = None
#     _, key_id = cc_show_pub_key(name)
#
#     if key_id:
#         raise Exception("keypair name already exists.")
#
#     with open(os.path.expanduser(pub_key)) as fh:
#         buff = fh.read()
#         pass
#
#     result = h.create_keypair(name, mode='user', public_key=buff, encrypt_method=_detected_ssh_public_key_type(pub_key))
#
#     return True if result['ret_code'] == 0 else False
#
#
# def cc_delete_pub_key(name):
#     h = cloud_init()
#
#     key_data = cc_show_pub_key(name)
#
#     key_name, key_id = key_data
#
#     if not key_id:
#         raise Exception("ssh key not exists.")
#
#     # detech key pair
#     instances = cc_show_instance_list('all')
#
#     h.detach_keypairs([key_id], instances)
#     h.delete_keypairs([key_id])
#
#     pass
#
#
# def cc_show_pub_key_list(search_word=None):
#     h = cloud_init()
#
#     result = h.describe_key_pairs(search_word=search_word)
#
#     names = []
#     key_ids = []
#
#     key_data = []
#
#     if result['total_count']:
#         key_data = [(v['keypair_name'], v['keypair_id']) for v in result['keypair_set']]
#
#     return key_data
#
#
# def cc_show_pub_key(name):
#     keys = cc_show_pub_key_list(name)
#
#     try:
#         compare = zip(*keys)[0]
#         pos = compare.index(name)
#     except:
#         pos = -1
#         pass
#
#     if pos > -1:
#         return keys[pos]
#
#     return None, None
#

