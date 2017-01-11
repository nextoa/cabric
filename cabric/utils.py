# -*- coding: utf-8 -*-


import os
import sys

from fabric.context_managers import cd as fabric_cd
from fabric.context_managers import lcd as fabric_lcd
from fabric.context_managers import settings as fabric_settings
from fabric.network import disconnect_all
from fabric.operations import local as fabric_local
from fabric.operations import run as fabric_run
from fabric.state import env_options, env
from fabric.state import output
from fabric.tasks import execute as fab_execute

from cabric.bridge import parse_options, update_output_levels, load_settings


# try:
#     from shlex import quote as cmd_quote
# except ImportError:
#     from pipes import quote as cmd_quote


def _is_network_error_ignored():
    return not env.use_exceptions_for['network'] and env.skip_bad_hosts


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


def put(local_path, remote_path):
    """
    ..todo::

        this should be improved.
        it may ignore .* file

    :param local_path:
    :param remote_path:
    :return:
    """
    if env.hosts:
        if os.path.isdir(local_path):
            local_path = local_path.rstrip('/') + '/'
            remote_path = remote_path.rstrip('/') + '/'
            fabric_local("prsync -r {2} {0} {1}".format(local_path, remote_path,
                                                        ' '.join(["-H %s" % v for v in env.hosts])))
        else:
            fabric_local("prsync {2} {0} {1}".format(local_path, remote_path,
                                                     ' '.join(["-H %s" % v for v in env.hosts])))

    else:
        fabric_local("cp -rf %s %s" % (local_path, remote_path))

    pass


def mirror_put(local_root, remote_path, validate=True):
    """
    mirror input

    use rsync instead fabric put.
    because fabric put is too slow.

    :param local_root:
    :param remote_path:
    :param validate:

    :return:
    """

    local_path = local_root + remote_path

    checks = [
        not os.path.exists(local_root),
        not os.path.exists(local_path),
    ]

    if validate:
        if True in checks:
            raise OSError("%s not exists" % local_path)

    # all path exists,then try upload or copy it
    if True not in checks:
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


def bind_hosts(fabric_root, select_env, parallel=False):
    """
    bind hosts from file
    :param fabric_root:
    :param select_env:
    :param parallel:
    :return:
    """

    machine_config = os.path.join(fabric_root, select_env + '.conf')

    if not os.path.exists(machine_config):
        raise OSError("%s not exist or permission denied." % machine_config)

    inner_options = ['-P'] if parallel else []

    parser, options, arguments = parse_options(inner_options)

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


def cd(path):
    if env.hosts:
        return fabric_cd(path)
    else:
        return fabric_lcd(path)
    pass


def run(cmd, user=None, capture=None, *args, **kwargs):
    """
    :param cmd: command to execute
    :param user: user mode will be ignore when we deploy on local machine.
    :param capture: in local machine, it will be True by default.
    :param args:
    :param kwargs:
    :return:
    """
    if env.hosts:
        if user:
            return fabric_run("su - %s -c '%s'" % (user, cmd))
        else:
            return fabric_run(cmd, *args, **kwargs)
    else:
        capture = True if capture is None else capture
        return fabric_local(cmd, capture=capture, *args, **kwargs)
    pass


def run_block(centos=None, mac=None, all=None, with_exception=True):
    """

    :param centos:
    :param macos:
    :param all:
    :return:
    """

    remote_os = get_platform()

    if remote_os == 'centos':
        if centos:
            centos()
        pass
    elif remote_os == 'mac':
        if mac:
            mac()
        pass
    else:
        if with_exception:
            raise NotImplemented("not support platform.")
        else:
            return False

    if all:
        all()

    return True


def execute(commands):
    results = []

    try:
        commands_to_run = [(v, [], {}, [], [], []) for v in commands]

        for name, args, kwargs, arg_hosts, arg_roles, arg_exclude_hosts in commands_to_run:
            results.append(fab_execute(name, hosts=arg_hosts, roles=arg_roles, exclude_hosts=arg_exclude_hosts, *args, **kwargs))
            pass
    except SystemExit:  # a number of internal functions might raise this one.
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

    return results


def get_platform():
    remote_os = run('uname')
    remote_os = remote_os.lower().strip("\n")

    if remote_os == 'darwin':
        return 'mac'
    elif remote_os == 'linux':
        distribute = run("gawk -F= '/^NAME/{print $2}' /etc/os-release")
        if 'centos' in distribute.lower():
            return 'centos'
        pass

    return 'unknown'


def get_home(user):
    with fabric_settings(warn_only=True):
        if run('cat /etc/passwd | grep "^%s:"' % user).failed:
            raise ValueError("User:%s not exists" % user)
        else:
            user_path = run("cat /etc/passwd | grep '^%s:' | awk -F ':' '{print $6}'" % user)
            return user_path
    pass


def get_git_host(address):
    host_begin = address.find('@')
    host_end = address.find(':')

    if host_begin <= 0 or host_end <= 0:
        raise ValueError('invalid git address to parse')

    return address[host_begin + 1:host_end].strip()


def get_repo():
    return fabric_local('git remote get-url origin --push', capture=True)


def exist_user(user):
    """
    check user exist or not
    :param user:
    :return:
    """

    with fabric_settings(warn_only=True):
        if run('cat /etc/passwd | grep ^%s:' % user).failed:
            return False
        else:
            return True

    pass


def exist_group(group):
    """
    check group exist or not
    :param group: group name
    :return:
    """

    with fabric_settings(warn_only=True):
        if run('cat /etc/group | grep ^%s:' % group).failed:
            return False
        else:
            return True

    pass


def known_host(address, user):
    """
    set ssh fingerprint
    :param address:domain or ip
    :param user:remote user name
    """

    user_path = get_home(user)
    command0 = 'grep %s %s/.ssh/known_hosts' % (address, user_path)
    command1 = 'ssh-keyscan %s >> %s/.ssh/known_hosts' % (address, user_path)
    command2 = 'sed -i -e "s/%s//g" %s/.ssh/known_hosts' % (address, user_path)

    if user:
        command0 = 'su - %s -c "%s"' % (user, command0)
        command1 = 'su - %s -c "%s"' % (user, command1)
        command2 = 'su - %s -c "%s"' % (user, command2)
        pass

    with fabric_settings(warn_only=True):
        if run(command0).failed:
            run(command1)
        else:
            # clean old record
            run(command2)
            run(command1)

    pass
