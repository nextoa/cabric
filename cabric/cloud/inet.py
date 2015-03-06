# -*- coding: utf-8 -*-


from cabric.cloud.core import *
from cabric.cloud.config import *
from cabric.cloud.key import *
from cabric.lib import *


# only use in develop for cabric
try:
    import qingcloud.iaas
except:

    pass


def cc_inet_find_all(search_word=None, tag="all"):
    """
    get inet list
    @todo currently this is only use to check name whether or not exists
    :return: cloud origin instance data
    """

    h = cloud_init()
    # h = qingcloud.iaas.connect_to_zone()

    result = h.describe_eips()

    data = []
    d = result.get('eip_set')

    filters = ['pending', 'available', 'associated', 'suspended']

    for v in d:
        if v.get('status') in filters:
            data.append(v)
            pass

    if search_word:
        compare = [v['eip_name'] for v in data]

        instances_list_or_int = cloud_name_match(search_word, compare)
        if isinstance(instances_list_or_int, list):
            data = [v for v in data if v['eip_name'] in instances_list_or_int]
        elif instances_list_or_int == -1:
            data = []
        else:
            data = [data[instances_list_or_int]]
        pass

    return data


def cc_inet_find_one(inet_name=None, inet_id=None, tag="all"):
    """
    get first match inet info
    if set inet_id and inet_name sametime, use inet_id
    :param inet_id:
    :param inet_name:
    :return: dict on success, NoneType on no inet found
    """

    if inet_id:
        inet_list = cc_inet_find_all(tag=tag)

        compare = [v['eip_id'] for v in inet_list]

        pos = cloud_name_match(inet_id, compare)

        if pos > -1:
            return inet_list[pos]
    else:
        inet_list = cc_inet_find_all(inet_name, tag=tag)
        if inet_list:
            return inet_list[0]

    pass


def cc_inet_create(name='router'):
    """
    create inet
    :param name:
    :return: None, raise expection on fail
    """
    h = cloud_init()

    if not name:
        print_error("limit name,please set a real name for your inet.")

    inet_id = cc_config_get('inet.' + name)

    # try to create inet if not exists
    inet_info = cc_inet_find_one(name)

    if inet_info and inet_id:
        print_debug("inet `{}' already exists.".format(name))
        return
    elif inet_info and not inet_id:
        inet_id = inet_info['eip_id']
    else:
        print_debug("inet `{}' will be create.".format(name))
        result = cloud_run(h.allocate_eips, func_kwargs=dict(bandwidth=1, eip_name=name), return_key='eips', hold_func=False)
        inet_id = result[0]

    print_debug("inet `{}' created: id:{}".format(name, inet_id))
    cc_config_set('inet.' + name, inet_id)
    cc_config_save()
    pass


def cc_inet_associate(instance_id, inet_id=None):
    # h = qingcloud.iaas.connect_to_zone()
    h = cloud_init()
    cloud_run(h.associate_eip, func_args=[inet_id, instance_id])
    pass


def cc_inet_dissociate(inet_id):
    # h = qingcloud.iaas.connect_to_zone()
    h = cloud_init()

    is_associated = cc_inet_find_one(inet_id=inet_id, tag="associated")

    if is_associated:
        cloud_run(h.dissociate_eips, func_args=[[inet_id]])

    pass


def cc_inet_release(inet_id):
    # h = qingcloud.iaas.connect_to_zone()
    h = cloud_init()

    is_available = cc_inet_find_one(inet_id=inet_id, tag="available")



    if is_available:
        cloud_run(h.release_eips, func_args=[[inet_id]])

    pass



def cc_inet_change_name(inet_id, new_name):
    # h = qingcloud.iaas.connect_to_zone()
    h = cloud_init()
    h.modify_eip_attributes(inet_id, new_name)
    pass



