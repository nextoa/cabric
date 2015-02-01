# -*- coding: utf-8 -*-

from cabric.lib import _detected_ssh_public_key_type

from cabric.env import ez_env
from cabric.lib import print_error, print_debug
from cabric.escape import *

import time

try:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError
except:
    from configparser import ConfigParser, NoSectionError, NoOptionError


def cloud_run(func, func_args=[], func_kwargs={}, return_key=None, strict=True, hold_func=None):
    """
    execute cloud operation
    :param func: cloud api function
    :param hold_func: jobs query fuction , if not set use  `ez_env.cloud_processor` set
    :param strict: true for wait jobs finish.
    :param return_key: get value from json respone
    :param func_args: cloud api function args
    :param func_kwargs: cloud api kwargs
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
    # if set return_key,set data
    if return_key:
        data = result[return_key]

    # if not strict ,return directly
    if not strict and result['ret_code']:
        return data

    # bind cloud processor function
    if hold_func is False:
        current_hold_func = False
    else:
        current_hold_func = hold_func if hold_func else ez_env.cc['processor']

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
                time.sleep(ez_env.cloud_hold_recyle)
            else:
                raise Exception(v)
            pass

            counter += 1
            print("." * counter)

        if stop:
            break
        pass

    return data


def cloud_init():
    """create connection


    :param cloud_class:
    :return: qingcloud.iaas.connection.APIConnection
    """

    if ez_env.cc['connection']:
        return ez_env.cc['connection']

    cloud_class = ez_env.cc.get('cloud_class')

    if not cloud_class:
        print_error("please set ez_env.cc.cloud_class.  e.g:`fab ez:*'")

    if cloud_class.__name__ != "qingcloud.iaas":
        print_error("currently,we only support qingcloud. http://www.qingcloud.com ")

    print("connect cloud use class:{}".format(cloud_class.__name__))
    connection = cloud_class.connect_to_zone(*ez_env.cloud)

    ez_env.cc['connection'] = connection
    ez_env.cc['processor'] = connection.describe_jobs
    ez_env.cc['sleep_time'] = 3
    ez_env.cc['config'] = cloud_config_init()

    return connection


def cloud_config_init(file='./config/cabric/cloud.conf'):
    """
    get cloud config
    :return:
    """
    parser = ConfigParser()
    parser.read(file)
    return parser


def cloud_config_guard():
    """
    basic valid for cloud_config
    :return:
    """

    if not isinstance(ez_env.cc['config'], ConfigParser):
        print_error("cloud config handler error, this must instance from ConfigParser object")

    return ez_env.cc['config']


def cloud_config_save(file='./config/cabric/cloud.conf'):
    """
    update cloud config
    :return:
    """

    parser = cloud_config_guard()

    with open(file, 'wb') as h:
        parser.write(h)


import re


def cloud_name_match(name, data):
    """
    when use regxp mode, will replace * to [a-z0-9_]
    use case-insensitive mode
    :param name:
    :param data:
    :return: return positon in search mode, return list in regxp mode on success
    """

    match_mode = "search"

    name = to_unicode(name.lower())

    data = filter(lambda x: to_unicode(x.lower()), data)

    if name.find('*') > -1:
        match_mode = "regxp"

    if match_mode == "search":
        if name in data:
            return data.index(name)
        else:
            return -1
    else:
        regxp = '^' + name.replace('*', '[a-z0-9_]*')

        data = filter(lambda x: re.findall(regxp, x), data)
        return data

    pass


def cloud_name_create(group, lives):
    """
    create new name with order
    :param group:
    :param lives:
    :return:
    """
    if not lives:
        return group + '01'

    lives.sort()
    last_id = lives.pop()[len(group):]
    return '{}{:02d}'.format(group, int(last_id) + 1)














