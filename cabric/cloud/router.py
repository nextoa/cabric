# -*- coding: utf-8 -*-


from cabric.cloud.core import *
from cabric.cloud.config import *
from cabric.cloud.key import *
from cabric.cloud.firewall import *

from cabric.lib import *



# only use in develop for cabric
try:
    import qingcloud.iaas
except:

    pass


def cc_router_find_all(search_word=None, tag="all"):
    """
    get router list
    @todo currently this is only use to check name whether or not exists
    :return: cloud origin instance data
    """

    h = cloud_init()
    # h = qingcloud.iaas.connect_to_zone()

    result = h.describe_routers()

    # this should have 1 vmnet at least
    data = []
    d = result.get('router_set')

    filters = ['pending', 'active', 'poweroffed', 'suspended']

    # if tag == 'start':
    # filters = ['running']
    # elif tag == 'stop':
    # filters = ['stopped']

    for v in d:
        if v.get('status') in filters:
            data.append(v)
            pass

    if search_word:
        compare = [v['router_name'] for v in data]

        instances_list_or_int = cloud_name_match(search_word, compare)
        if isinstance(instances_list_or_int, list):
            data = [v for v in data if v['router_name'] in instances_list_or_int]
        elif instances_list_or_int == -1:
            data = []
        else:
            data = [data[instances_list_or_int]]
        pass

    return data


def cc_router_find_one(router_name=None, router_id=None):
    """
    get first match router info
    if set router_id and router_name sametime, use router_id
    :param router_id:
    :param router_name:
    :return: dict on success, NoneType on no router found
    """

    if router_id:
        router_list = cc_router_find_all()

        compare = [v['router_id'] for v in router_list]

        pos = cloud_name_match(router_id, compare)

        if pos > -1:
            return router_list[pos]
    else:
        router_list = cc_router_find_all(router_name)
        if router_list:
            return router_list[0]

    pass


def cc_router_create(name='default', firewall_name="default"):
    """
    create router
    :param name:
    :return: None, raise expection on fail
    """
    h = cloud_init()

    if not name:
        print_error("limit name,please set a real name for your router.")

    router_id = cc_config_get('router.' + name)

    # try to create router if not exists
    router_info = cc_router_find_one(name)

    if router_info and router_id:
        print_debug("router `{}' already exists.".format(name))
        router_id = router_info['router_id']
    elif router_info and not router_id:
        router_id = router_info['router_id']
    else:
        print_debug("router `{}' will be create.".format(name))
        result = cloud_run(h.create_routers, func_kwargs=dict(router_name=name), return_key='routers')
        router_id = result[0]

    cc_config_set('router.' + name, router_id)
    cc_config_save()

    # powerup router
    print_debug("try powerup router `{}'".format(name))
    # h = qingcloud.iaas.connect_to_zone()
    try:
        cloud_run(h.poweron_routers, [[router_id]])
    except Exception as e:
        print_debug(e)
        pass

    cc_firewall_rule_route(firewall_name)
    pass


def cc_router_bind_lan(router_name="default", lan_name="default", ip_network=None):
    """
    bind lan
    :return:
    """

    h = cloud_init()

    router_id = cc_config_get('router.' + router_name)
    lan_id = cc_config_get('lan.' + lan_name)

    ip_network = ip_network or cc_config_get('global.lan', "192.168.1.0/24")

    if not router_id:
        print_error("can't find router:`{}' before bind router-lan".format(router_name))

    if not lan_id:
        print_error("can't find LAN:{} before bind router-lan,you must set a LAN".format(lan_name))

    print_debug("router `{}' will bind lan `{}',ip:{}".format(router_name, lan_name, ip_network))

    try:
        cloud_run(h.join_router, func_kwargs=dict(router=router_id, ip_network=ip_network, vxnet=lan_id))
    except Exception as e:
        if str(e).find(" already join router"):
            print_debug("router `{}' already bind to LAN `{}'".format(router_name, lan_name))
        else:
            raise
        pass

    pass


def cc_router_bind_internet(router_name="default", inet_name="router"):
    """
    bind internet
    :return:
    """

    h = cloud_init()

    router_id = cc_config_get('router.' + router_name)
    inet_id = cc_config_get('inet.' + inet_name)

    if not router_id:
        print_error("can't find router:`{}' before bind router-inet".format(router_name))

    if not inet_id:
        print_error("can't find inet:`{}' before bind router-inet,you must set a inet".format(inet_name))

    router_info = cc_router_find_one(router_name)
    if router_info and router_info['eip']['eip_addr']:
        if router_info['eip']['eip_id'] == inet_id:
            print_debug("router `{}' already bind to public ip:`{}'.".format(router_name, inet_name))
        else:
            print_debug("router `{}' already bind a public ip {},please dissociate it first".format(router_name, router_info['eip']['eip_addr']))
        return

    print_debug("router `{}' will bind to internet `{}'".format(router_name, inet_name))

    # h = qingcloud.iaas.connect_to_zone()

    cloud_run(h.modify_router_attributes, func_kwargs=dict(router=router_id, eip=inet_id), hold_func=False)
    cloud_run(h.update_routers, [[router_id]])
    pass


def cc_router_bind_vpn(router_name="default"):
    """
    bind vpn
    :return:
    """

    h = cloud_init()

    # h = qingcloud.iaas.connect_to_zone()

    router_id = cc_config_get('router.' + router_name)

    if not router_id:
        print_error("can't find router:`{}' before bind router-inet".format(router_name))

    print_debug("router `{}' will try to open vpn ".format(router_name))

    try:
        cloud_run(h.add_router_statics, (str(router_id), [{
                                                              'static_type': 2,
                                                              'val1': "openvpn",
                                                          }]), hold_func=False)

        cloud_run(h.update_routers, [[router_id]])
    except Exception as e:
        if str(e).find(" VPN already enabled"):
            print_debug("router `{}' already enable VPN ".format(router_name))
        else:
            raise
        pass

    for i in reversed(range(5, 10)):
        print("#" * i)
        pass
    print(" ")
    print("please open your brower and vist: `https://console.qingcloud.com/{}/routers/{}/#' to download your vpn certificate and Install it".format(ez_env.cloud[0], router_id))
    print(" ")
    for i in range(5, 10):
        print("#" * i)
        pass


    # result = input("Install Finished?[yes/no]:")

    # while True:
    # result = input("Install Finished?[yes/no]:")
    #
    # if result.lower().strip() == "yes":
    # break
    # pass

    print("VPN initial finished")
    pass



