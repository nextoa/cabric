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



