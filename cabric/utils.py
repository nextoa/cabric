# -*- coding: utf-8 -*-


import os
import sys

from fabric.state import env_options, env
from fabric.main import parse_options, update_output_levels, load_settings, parse_arguments
from fabric.api import put
from fabric.api import run as fabric_run
from fabric.api import local as fabric_local
from fabric.tasks import execute as fabric_execute
from fabric.network import disconnect_all
from fabric.state import output


def get_roots(project):
    """
    get relate config root of cabric.

    ..note::

        if config root or sub root not exist. it will raise OSError

    :return: tuple package_root,stage_root,fabric_root
    """

    root = os.path.join(project, 'config')

    if not os.path.exists(root):
        raise OSError("%s not exists or permission denied" % root)

    package_root = os.path.join(root, 'cabric')
    config_root = os.path.join(root, 'stage')
    fabric_root = os.path.join(root, 'fabric')

    roots = (package_root, config_root, fabric_root)

    for sub_root in roots:
        if not os.path.exists(sub_root):
            raise OSError("%s not exists or permission denied" % sub_root)
        pass

    return roots


def mirror_put(local_root, remote_path, validate=True):
    """
    mirror input
    :param local_root:
    :param remote_path:
    :param validate:

    :return:
    """

    local_path = local_root + remote_path

    if validate:
        checks = [
            not os.path.exists(local_root),
            not os.path.exists(local_path),
        ]

        if True in checks:
            raise OSError("%s not exists" % local_path)

    put(local_path, remote_path)
    pass


def parse_hosts(file):
    """
    :param file:
    :return:
    """

    file = os.path.expanduser(file)

    with open(file, 'r') as fp:
        buffer = fp.read()

    host_list = buffer.strip("\n").split("\n")
    machines = []
    for v in host_list[:]:
        addr = v.strip()
        if addr.find('#') == 0:
            continue

        # support inline comment
        machines.append(addr.split("#")[0].strip())

    return machines


def bind_hosts(fabric_root, select_env):
    """
    bind hosts from file
    :param fabric_root:
    :param select_env:
    :return:
    """

    machine_config = os.path.join(fabric_root, select_env + '.conf')

    if not os.path.exists(machine_config):
        raise OSError("%s not exist or permission denied." % machine_config)

    parser, options, arguments = parse_options()

    # Handle regular args vs -- args
    arguments = parser.largs
    remainder_arguments = parser.rargs

    for option in env_options:
        env[option.dest] = getattr(options, option.dest)

    env.hosts = parse_hosts(machine_config)
    env.use_ssh_config = True
    env.roledefs[select_env] = env.hosts

    for key in ['hosts', 'roles', 'exclude_hosts']:
        if key in env and isinstance(env[key], basestring):
            env[key] = env[key].split(',')

    # Handle output control level show/hide
    update_output_levels(show=options.show, hide=options.hide)
    env.update(load_settings(env.rcfile))

    return machine_config


def run(*args, **kwargs):
    if env.hosts:
        return fabric_run(*args, **kwargs)
    else:
        return fabric_local(*args, **kwargs)
    pass


def execute(commands):
    try:
        commands_to_run = [(v, [], {}, [], [], []) for v in commands]

        for name, args, kwargs, arg_hosts, arg_roles, arg_exclude_hosts in commands_to_run:
            fabric_execute(
                    name,
                    hosts=arg_hosts,
                    roles=arg_roles,
                    exclude_hosts=arg_exclude_hosts,
                    *args, **kwargs
            )

    except SystemExit:
        # a number of internal functions might raise this one.
        raise
    except KeyboardInterrupt:
        if output.status:
            sys.stderr.write("\nStopped.\n")
        sys.exit(1)
    except:
        sys.excepthook(*sys.exc_info())
        # we might leave stale threads if we don't explicitly exit()
        sys.exit(1)
    finally:
        disconnect_all()
    pass
