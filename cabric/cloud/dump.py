# -*- coding: utf-8 -*-

from cabric.cloud.core import *
from cabric.cloud.config import *
from cabric.cloud.instance import *

from cabric.lib import print_debug, print_error

import re


def cc_dump(names, to, hold=True):
    """
    dump instanse to config
    :param names:
                legal syntax example
                    web01-03#web*#web01#web02
    :return:
    """

    origin_list = names.split('#')
    instance_name_list = set()

    # build instance name list
    def parse_range(x):
        if x.find('-') > -1:
            x = x.lower()
            match_range = re.findall("([a-z]+)([0-9]+)-([0-9]+)", x)

            if not match_range:
                print_error("illegal syntax. use `[a-z]+[0-9]+-[0-9]+',e.g:web01-03")

            match = match_range[0]

            begin = int(match[1])
            end = int(match[2]) + 1

            for i in range(begin, end):
                instance_name_list.add('{}{:02d}'.format(match[0], i))
                pass

            return
        instance_name_list.add(x)
        pass

    map(parse_range, origin_list)
    instance_name_list = set(v for v in instance_name_list if v)

    print_debug("dump matched names:{}".format(instance_name_list))

    instance_list = set()

    def find_instances(x):
        if x.find('*'):
            instance_infos = cc_instance_find_all(x)
            for v in instance_infos:
                instance_list.add(v['instance_id'])
        else:
            instance_info = cc_instance_find_one(x)
            if instance_info:
                instance_list.add(instance_info['instance_id'])
            else:
                print("Warning:can't find instance {}.".format(x))

        pass

    map(find_instances, instance_name_list)

    print_debug("dump matched instances:{}".format(instance_list))

    # get remote ip list
    remote_list = set()

    def build_host(instance_id):
        tries = 100
        curr_tries = 0
        private_ip = None

        while True:
            curr_tries += 1
            if curr_tries > tries:
                print_error("get private ip fail,please check your instance config.")

            instance_info = cc_instance_find_one(instance_id=instance_id)
            private_ip = instance_info['vxnets'][0]['private_ip']

            if not private_ip:
                print("Wait for init private IP...")
                time.sleep(5)
            else:
                break
            pass

        return private_ip


    for v in instance_list:
        remote_list.add('root@' + build_host(v))

    print_debug("dump matched hosts:{}".format(remote_list))

    # write to file
    with open('./config/fabric/{}.conf'.format(to), 'w') as fh:
        fh.write("####Create By Cabric#####\n\n" + "\n".join(remote_list))

    pass

