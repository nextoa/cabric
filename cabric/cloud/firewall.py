# -*- coding: utf-8 -*-

from cabric.cloud.core import *
from cabric.cloud.config import *
from cabric.lib import *

# only use in develop for cabric
try:
    import qingcloud.iaas
except:

    pass


def cc_firewall_find_all(search_word=None, verbose=0):
    """
    get firewall list
    @todo currently this is only use to check name whether or not exists
    :return: cloud origin instance data
    """

    h = cloud_init()
    # h = qingcloud.iaas.connect_to_zone()

    result = h.describe_security_groups(verbose=verbose)

    # this should have 1 firewall at least
    data = result.get('security_group_set')

    if search_word:
        compare = [v['security_group_name'] for v in data]

        instances_list_or_int = cloud_name_match(search_word, compare)
        if isinstance(instances_list_or_int, list):
            data = [v for v in data if v['security_group_name'] in instances_list_or_int]
        elif instances_list_or_int == -1:
            data = []
        else:
            data = [data[instances_list_or_int]]
        pass

    return data


def cc_firewall_find_one(firewall_name=None, firewall_id=None):
    """
    get first match firewall info
    if set firewall_id and firewall_name sametime, use firewall_id
    :param firewall_id:
    :param firewall_name:
    :return: dict on success, NoneType on no firewall found
    """

    if firewall_id:
        firewall_list = cc_firewall_find_all()

        compare = [v['security_group_id'] for v in firewall_list]

        pos = cloud_name_match(firewall_id, compare)

        if pos > -1:
            return firewall_list[pos]
    else:
        firewall_list = cc_firewall_find_all(firewall_name)
        if firewall_list:
            return firewall_list[0]

    pass


def cc_firewall_create(name='load_balancer'):
    """
    create firewall
    :param name:
    :return: None, raise expection on fail
    """
    h = cloud_init()

    if not name:
        print_error("limit name,please set a real name for your firewall.")

    # try to create firewall if not exists
    firewall_info = cc_firewall_find_one(name)

    if firewall_info:
        print_debug("firewall `{}' already exists.".format(name))
        return
    else:
        print_debug("firewall `{}' will be create.".format(name))
        result = cloud_run(h.create_security_group, func_kwargs=dict(security_group_name=name), return_key='security_group_id', hold_func=False)
        firewall_id = result

    cc_config_set('firewall.' + name, firewall_id)
    cc_config_save()
    pass


def cc_firewall_rule_basic(firewall_name="default"):
    """
    create rule
    :param name: 
    :return:
    """

    h = cloud_init()

    if not firewall_name:
        print_error("limit name,please set a real name for your firewall.")

    firewall_id = cc_config_get('firewall.' + firewall_name)

    # try to create default firewall if not exists
    if not firewall_id and firewall_name == "default":
        print_debug("match default firewall")
        firewall_info = cc_firewall_find_one("default security group")
        firewall_id = firewall_info['security_group_id']
        cc_config_set('firewall.' + firewall_name, firewall_id)
        pass
    elif firewall_id:
        firewall_info = cc_firewall_find_one(firewall_id=firewall_id)
    else:
        print_error("can't find firewall:`{}'".format(firewall_name))

    if not firewall_info['is_applied']:
        print_debug("firewall has uncomit rule.begin to commit...")
        cloud_run(h.apply_security_group, [firewall_id])

    firewall_rules = cloud_run(h.describe_security_group_rules, [firewall_id], return_key='security_group_rule_set', hold_func=False)

    return firewall_id, firewall_rules


def cc_firewall_rule_route(firewall_name="default"):
    h = cloud_init()
    firewall_id, firewall_rules = cc_firewall_rule_basic(firewall_name)

    match = ['Web Services', 'VPN']

    rules = [
        {
            'protocol': 'tcp',
            'priority': 0,
            'security_group_rule_name': match[0],
            'action': 'accept',
            'direction': 0,
            'val1': 7000,
            'val2': 12000,
        },

        {
            'protocol': 'udp',
            'priority': 2,
            'security_group_rule_name': match[1],
            'action': 'accept',
            'direction': 0,
            'val1': 1194,
            'val2': 1194,
        }
    ]

    exists_key = set()

    def match_rule(x):
        value = x['security_group_rule_name']
        if value in match:
            print("{} rule matched,skip apply it.".format(value))
            exists_key.add(value)
        pass

    filter(match_rule, firewall_rules)

    rules = [x for x in rules if x['security_group_rule_name'] not in exists_key]

    if not rules:
        print_debug("no rules should apply,skip.")
        return

    print_debug("begin to bind firewall router rule.")
    cloud_run(h.add_security_group_rules, (firewall_id, rules), hold_func=False)
    cloud_run(h.apply_security_group, [firewall_id])
    pass


def cc_firewall_rule_load_balancer(firewall_name="load_balancer"):
    """
    bind rule for load balancer
    :param firewall_name:
    :return:
    """

    if firewall_name == "default":
        print_error("load balancer firewall rule does'nt allow to bind {}.".format(firewall_name))

    h = cloud_init()
    firewall_id, firewall_rules = cc_firewall_rule_basic(firewall_name)

    match = ['HTTP', 'HTTPS']

    rules = [
        {
            'protocol': 'tcp',
            'priority': 0,
            'security_group_rule_name': match[0],
            'action': 'accept',
            'direction': 0,
            'val1': 80,
            'val2': 80,
        },

        {
            'protocol': 'tcp',
            'priority': 1,
            'security_group_rule_name': match[1],
            'action': 'accept',
            'direction': 0,
            'val1': 443,
            'val2': 443,
        }
    ]

    exists_key = set()

    def match_rule(x):
        value = x['security_group_rule_name']
        if value in match:
            print("{} rule matched,skip apply it.".format(value))
            exists_key.add(value)
        pass

    filter(match_rule, firewall_rules)

    rules = [x for x in rules if x['security_group_rule_name'] not in exists_key]

    if not rules:
        print_debug("no rules should apply,skip.")
        return

    print_debug("begin to bind firewall load balancer rule.")
    cloud_run(h.add_security_group_rules, (firewall_id, rules), hold_func=False)
    cloud_run(h.apply_security_group, [firewall_id])
    pass


