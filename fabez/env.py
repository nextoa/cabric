# -*- coding: utf-8 -*-

import os
from fabric.api import *
from fabric.utils import _AttributeDict

import time


ez_env = _AttributeDict({
    'group': None,
    'roles': None,
    'cloud': None,
    'cloud_processor': None,
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


def bind_hosts(curr, routes=None):
    """
    bind hosts from file
    :param curr:
    :param routes:
    :return:
    """

    if not routes:
        current_path = './config/fabez'

        files = os.listdir(current_path)

        routes = {}

        for f in files:

            if f.endswith('conf'):
                k = f.rsplit('.')[0]
                v = os.path.join(current_path, f)
                routes[k] = v
                pass

            pass

        pass

    ez_env.group = curr
    ez_env.roles = {}

    for k, v in routes.items():
        if k == curr:
            env.hosts = _pssh(v)
            env.use_ssh_config = True
        ez_env.roles[k] = _pssh(v)
        pass
    pass


def bind_cloud(cloud_options):
    ez_env.cloud = cloud_options
    pass






