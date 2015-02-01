# -*- coding: utf-8 -*-


from cabric.cloud.core import *
from cabric.cloud.config import *
import cabric.cloud.key
from cabric.lib import *


def cc_instance_find_all(search_word=None, tag='all'):
    """
    get instance list
    *Note* search rule use `cloud_name_match' not cloud build-in feature
    :return: cloud origin instance data
    """

    h = cloud_init()
    result = h.describe_instances()

    data = []

    d = result.get('instance_set')

    filters = ['running', 'stopped', 'pending', 'suspended']

    if tag == 'start':
        filters = ['running']
    elif tag == 'stop':
        filters = ['stopped', 'pending', 'suspended']

    for v in d:
        if v.get('status') in filters:
            data.append(v)
            pass

    if search_word:
        compare = [v['instance_name'] for v in data]
        instances_list_or_int = cloud_name_match(search_word, compare)
        if isinstance(instances_list_or_int, list):
            data = [v for v in data if v['instance_name'] in instances_list_or_int]
        elif instances_list_or_int == -1:
            data = []
        else:
            data = [data[instances_list_or_int]]
        pass

    return data


def cc_instance_find_one(instance_name=None, instance_id=None):
    """
    get first match instance info
    if set instance_id and instance_name sametime, use instance_id
    :param instance_id:
    :param instance_name:
    :return: dict on success, NoneType on no instance found
    """

    if instance_id:
        instance_list = cc_instance_find_all()

        compare = [v['instance_id'] for v in instance_list]
        pos = cloud_name_match(instance_id, compare)
        if pos > -1:
            return instance_list[pos]
    else:
        instance_list = cc_instance_find_all(instance_name)
        if instance_list:
            return instance_list[0]

    pass


def cc_instance_create(group, owner=None, lan_name='default', part_time=False, image_id=None, instance_type=None):
    """
    @todo support user image_id
    :return:
    """
    h = cloud_init()

    # get instance_type
    instance_type = instance_type or cc_config_get('instance_type.' + group, 'c1m1')

    # get image_id
    image_id = image_id or cc_config_get('image.' + group, 'centos65x64d')

    # get current part_time instances
    parttime_instances = cc_config_lget('parttime.' + group)

    # get network
    lan_id = cc_config_get('lan.' + lan_name)
    if not lan_id:
        print_error("please set your LAN first. if you don't have,use `cc_lan_create()' first.")

    # get key_name
    key_name = owner or cc_config_get('global.author')
    key_name, key_id = cabric.cloud.key.cc_key_find_one(key_name)

    # upload new key,when user not found
    if not key_id:
        print_debug("key `{}' not found,upload it now.".format(key_name))
        key_path = cc_config_get('global', 'pub_key') or '~/.ssh/id_rsa.pub'

        if not os.path.exists(os.path.expanduser(key_path)):
            print_error("can find public key,please add it or custom in cloud.conf file,current path:{}".format(key_path))

        cc_key_create(key_name, key_path)


    # set instances name
    exist_instances = cc_instance_find_all(group + '*')
    exist_names = [v['instance_name'] for v in exist_instances]
    new_name = cloud_name_create(group, exist_names)

    instances = cloud_run(h.run_instances, func_kwargs=dict(image_id=image_id, instance_type=instance_type, instance_name=new_name, vxnets=[lan_id], login_mode='keypair', login_keypair=key_id),
                          return_key='instances', hold_func=False)

    if part_time:
        parttime_instances = set(parttime_instances)
        parttime_instances.add(instances['instances_id'])
        cc_config_lset('parttime.' + group, parttime_instances)
        cc_config_save()

    pass


def cc_instance_parttime_start(group):
    """
    start parttime instances
    :param group:
    :return:
    """

    h = cloud_init()

    instances = cc_config_lget('parttime.' + group)

    if not instances:
        print("no part-time instances found. skip")
        return

    cloud_run(h.start_instances, func_args=[
        list(instances)
    ])

    pass


def cc_instance_stop_part_time(group):
    """
    stop part-time instances
    :param group:
    :return:
    """
    h = cloud_init()

    instances = cc_config_lget('parttime.' + group)

    if not instances:
        print("no part-time instances found. skip")
        return

    cloud_run(h.stop_instances, func_args=[
        list(instances)
    ])
    pass




def cc_instance_port_forward(https=False):
    """
    only allow to forward 80 or 443
    :return:
    """

    port = 80

    if https:
        port = 443



    pass




