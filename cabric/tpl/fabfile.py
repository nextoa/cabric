# -*- coding: utf-8 -*-

from fabric.api import *
from cabric.env import *
from cabric.api import *

import os


def ez(curr):

    # to specify routes
    # routes = {
    #     'dev': os.path.dirname(__file__) + '{0}/dev.conf',
    #     'beta': os.path.dirname(__file__) + '{0}/beta.conf',
    #     'ol': os.path.dirname(__file__) + '{0}/online.conf',
    # }
    #
    # bind_hosts(curr, routes)

    # create routes auto
    bind_hosts(curr)

    # use cloud feature, if you have multiple cloud data center, set bind_cloud here
    # bind_cloud(['pek2','app_key','app_secret'],CLOUD_CLASS)
    pass


def hello_fabric():
    local('echo "You can delete this function after initial it."')
    pass


def upgrade(tag=None, clean=False):
    """
    this function must contain `tag` and `clean` options
    :param tag:
    :param clean:
    :return:
    """

    root = '/tmp/cabric'  # repo deploy path
    repo = 'https://github.com/baixing/cabric.git'  # repo demo

    if clean:
        run('rm -rf %s' % root)
        pass

    if ez_env.group == 'ol':
        cmd_git(root, repo, branch='master', tag=tag)
        pass
    elif ez_env.group == 'beta':
        cmd_git(root, repo, branch='beta', tag=tag)
        pass
    # you should create branch and dev.conf files
    elif ez_env.group == 'dev':
        cmd_git(root, repo, branch='dev', tag=tag)
        pass
    else:
        print("[warn]:can't find default config,use master.")
        cmd_git(root, repo, branch='master', tag=tag)
        pass

    pass



# currently, cloud deploy feature only support qingcloud
try:
    import qingcloud.iaas
    # use cloud feature, if you have multiple cloud data center,comment it and set it in `ez` inside.
    bind_cloud(["pek2", "APP-KEY", "APP-SECRET"], qingcloud.iaas)
except:
    print("can't find qingcloud-sdk, if you don't want to use cloud feature,remove this code")
    pass



def init_datacenter():
    """
    create datacenter
    :return:
    """
    # create key
    cc_key_create()
    # create lan
    cc_lan_create()
    # create public ip
    cc_inet_create()
    # create router
    cc_router_create()
    # bind router to lan
    cc_router_bind_lan()
    # bind router to public ip
    cc_router_bind_internet()

    # todo create load balancer

    pass


def init_instance(group, nums=1, part_time=False):
    """
    create instance
    :param group:
    :param nums:
    :param part_time:
    :return:
    """
    try:
        nums = int(nums)
    except:
        nums = 1

    for i in range(0, nums):
        cc_instance_create(group, part_time=part_time)

    pass


def init_parttime_instance(group, nums=1):
    """
    create part-time
    :param group:
    :param nums:
    :return:
    """
    return init_instance(group, nums=nums, part_time=True)



