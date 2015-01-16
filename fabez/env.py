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
    'cloud_handler': None,
    'cloud_active': None,
    'debug': None,
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

                if k == 'online':
                    k = 'ol'
                    pass

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
            pass
        if k == 'online':
            k = 'ol'
            pass
        ez_env.roles[k] = _pssh(v)
        env.roledefs[k] = ez_env.roles[k]
        pass
    pass


def bind_cloud(cloud_options, handler=None):
    ez_env.cloud = cloud_options

    if handler:
        ez_env.cloud_handler = handler

    pass


from fabric.main import list_commands, _task_names, _normal_list, _nested_list


def help():
    # print("called!")

    commands = list_commands(None, "nested")

    support_type = ['cmd', 'cloud', 'classic', 'config', 'io', 'py', 'git']
    ignore = ['Dumper', 'Loader', 'bind_cloud', 'bind_hosts', 'dump', 'dump_codes']
    origin = ['Available commands:']

    print(commands)

    # commands.split("\n")

    return

    for c in commands_buff:

        compare = c.strip()

        print(compare)

        if compare in ignore:
            continue

        if compare in origin:
            print(c)
            continue

        # print("    " + c)
        pass

        #
        # if format_ == "short":
        # return _task_names(state.commands)
        # # Otherwise, handle more verbose modes
        # result = []
        # # Docstring at top, if applicable
        # if docstring:
        # trailer = "\n" if not docstring.endswith("\n") else ""
        # result.append(docstring + trailer)
        # header = COMMANDS_HEADER
        # if format_ == "nested":
        # header += NESTED_REMINDER
        # result.append(header + ":\n")
        # c = _normal_list() if format_ == "normal" else _nested_list(state.commands)
        # result.extend(c)
        # return result






