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


def cc_lan_find_all(search_word=None):
    """
    get lan list
    @todo currently this is only use to check name whether or not exists
    :return: cloud origin instance data
    """

    h = cloud_init()
    # h = qingcloud.iaas.connect_to_zone()

    result = h.describe_vxnets()

    # this should have 1 vmnet at least
    data = result.get('vxnet_set')

    if search_word:
        compare = [v['vxnet_name'] for v in data]

        instances_list_or_int = cloud_name_match(search_word, compare)
        if isinstance(instances_list_or_int, list):
            data = [v for v in data if v['vxnet_name'] in instances_list_or_int]
        elif instances_list_or_int == -1:
            data = []
        else:
            data = [data[instances_list_or_int]]
        pass

    return data


def cc_lan_find_one(lan_name=None, lan_id=None):
    """
    get first match lan info
    if set lan_id and lan_name sametime, use lan_id
    :param lan_id:
    :param lan_name:
    :return: dict on success, NoneType on no lan found
    """

    if lan_id:
        lan_list = cc_lan_find_all()

        compare = [v['vxnet_id'] for v in lan_list]

        pos = cloud_name_match(lan_id, compare)

        if pos > -1:
            return lan_list[pos]
    else:
        lan_list = cc_lan_find_all(lan_name)
        if lan_list:
            return lan_list[0]

    pass


def cc_lan_create(name='default'):
    """
    create lan
    :param name:
    :return: None, raise expection on fail
    """
    h = cloud_init()

    if not name:
        print_error("limit name,please set a real name for your LAN.")

    vxnet_id = cc_config_get('lan.' + name)

    if cc_lan_find_one(lan_id=vxnet_id):
        print_debug("lan {} already exists.".format(vxnet_id))
        return

    print_debug("lan `{}' will be create.".format(name))

    result = h.create_vxnets(name)

    if result['ret_code']:
        raise Exception(result)

    vxnet_id = result['vxnets'][0]
    cc_config_set('lan.' + name, vxnet_id)
    cc_config_save()
    pass





