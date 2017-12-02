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

    project = os.path.expanduser(project)

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
    local_path = os.path.expanduser(local_path)

    if env.host_string:

        rsync_bin = fabric_local('which rsync', capture=True)
        rsync = os.path.basename(rsync_bin)

        if not rsync:
            raise IOError("rsync not exist.please install it.")

        tpl = str('%(bin)s -e ssh%(port_str)s%(recursive_str)s '
                  '-v %(local_path)s %(host)s:%(remote_path)s')
        port = int(env.host_string[
                   env.host_string.find(':') + 1:]) if env.host_string.find(
            ':') > -1 else 22

        host = env.host_string[
               0:env.host_string.find(':')] if env.host_string.find(
            ':') > -1 else env.host_string

        port_str = ' %s' % port
        recursive_str = ''

        if os.path.isdir(local_path):
            local_path = local_path.rstrip('/') + '/'
            remote_path = remote_path.rstrip('/') + '/'
            recursive_str = ' -r'
            pass

        cmd = tpl % {
            'bin': rsync,
            'local_path': local_path,
            'remote_path': remote_path,
            'recursive_str': recursive_str,
            'port_str': port_str if port != 22 else '',
            'host': host
        }
        fabric_local(cmd)
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
    :return: machines and names pairs
    """

    file = os.path.expanduser(file)

    with open(file, 'r') as fp:
        buffer = fp.read()

    host_list = buffer.strip("\n").split("\n")
    machines = []
    names = []
    for v in host_list[:]:
        addr = v.strip()
        if not addr or addr.find('#') == 0:
            continue

        if addr.find('##') > 0:
            pairs = addr.split("#")
            machines.append(pairs[0].strip())
            names.append(pairs[-1].strip())
            pass
        else:
            machines.append(addr.split("#")[0].strip())
            names.append(None)

    return machines, names


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
        raise OSError("%s not exist." % machine_config)

    if not os.access(machine_config, os.R_OK):
        raise OSError("access %s permission denied." % machine_config)

    inner_options = ['-P'] if parallel else []

    parser, options, arguments = parse_options(inner_options)

    # Handle regular args vs -- args
    arguments = parser.largs
    remainder_arguments = parser.rargs

    for option in env_options:
        env[option.dest] = getattr(options, option.dest)

    env.hosts, env.host_names = parse_hosts(machine_config)
    env.use_ssh_config = True
    env.roledefs[select_env] = env.hosts

    for key in ['hosts', 'roles', 'exclude_hosts']:
        if key in env and isinstance(env[key], basestring):
            env[key] = env[key].split(',')

    # Handle output control level show/hide
    update_output_levels(show=options.show, hide=options.hide)
    env.update(load_settings(env.rcfile))

    for v in env.hosts:
        flag_postion = v.find('@')

        if flag_postion > -1:
            host = v[flag_postion + 1:]
        else:
            host = v
            pass
        known_host(host, local_mode=True, clean=False)
        pass

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

        for name, args, kwargs, arg_hosts, arg_roles, arg_exclude_hosts \
            in commands_to_run:
            results.append(fab_execute(name, hosts=arg_hosts, roles=arg_roles,
                                       exclude_hosts=arg_exclude_hosts, *args,
                                       **kwargs))
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
        return 'centos'
        # not all os has this file
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
            user_path = run("cat /etc/passwd |"
                            " grep '^%s:' |"
                            " awk -F ':' '{print $6}'" % user)
            return user_path
    pass


def get_git_host(address):
    host_begin = address.find('@')
    host_end = address.find(':')

    if host_begin <= 0 or host_end <= 0:
        raise ValueError('invalid git address to parse')

    return address[host_begin + 1:host_end].strip()


def get_repo():
    path = os.getcwd()
    if os.path.exists(os.path.join(path, '.git')):
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


def known_host(address, user=None, local_mode=False, clean=True):
    """
    set ssh fingerprint
    :param address:domain or ip
    :param user:remote user name
    :param local_mode: set known_host for localhost,default is False
    :param clean: clean exist record,default is True
    """

    user_path = '~' if local_mode else get_home(user)
    command0 = 'grep "%s " %s/.ssh/known_hosts' % (address, user_path)
    command1 = 'ssh-keyscan %s >> %s/.ssh/known_hosts' % (address, user_path)
    command2 = 'sed -i -e "s/%s//g" %s/.ssh/known_hosts' % (address, user_path)

    commander = fabric_local if local_mode else run

    if user:
        command0 = 'su - %s -c "%s"' % (user, command0)
        command1 = 'su - %s -c "%s"' % (user, command1)
        command2 = 'su - %s -c "%s"' % (user, command2)
        pass

    with fabric_settings(warn_only=True):
        if commander(command0).failed:
            commander(command1)
        else:
            if clean:
                # clean old record
                commander(command2)
                commander(command1)
                pass
            pass
        pass
    pass


def current_machine(position):
    try:
        if env.host_string == env.hosts[position]:
            return True
    except IndexError:
        pass

    return False
