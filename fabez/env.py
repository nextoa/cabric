# -*- coding: utf-8 -*-

import os
from fabric.api import *
from fabric.utils import _AttributeDict

import time


ez_env = _AttributeDict({
    'group': None,
    'cloud': None,
    'cloud_processor':None,
})


def _pssh(file):
    """
    Parse pssh-like file
    :param file:
    """
    file = os.path.realpath(os.path.expanduser(file))

    with open(file, 'r') as fp:
        buffer = fp.read()

    host_list = buffer.strip("\n").split("\n")
    machines = []
    for addr in host_list[:]:
        addr.strip()
        if addr.find('#') == -1:
            machines.append(addr)

    return machines


def _bind_pssh(file):
    """
    Bind env from pssh-like file
    :param file:
    """
    env.hosts = _pssh(file)
    env.use_ssh_config = True


def bind_hosts(curr, routes):
    """
    bind hosts from file
    :param curr:
    :param routes:
    :return:
    """

    ez_env.group = curr

    for k, v in routes.items():
        if k == curr:
            _bind_pssh(v)
            break
        pass
    pass


def bind_cloud(cloud_options):
    ez_env.cloud = cloud_options
    pass



def bind_cloud_processor(func=None):
    ez_env.cloud_processor=func
    pass




