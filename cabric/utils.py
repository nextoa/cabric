# -*- coding: utf-8 -*-


import os
import sys

from fabric.state import env_options, env
from fabric.main import parse_options, update_output_levels, load_settings, parse_arguments
from fabric.api import put
from fabric.api import run as fabric_run
from fabric.api import local as fabric_local
from fabric.job_queue import JobQueue
from fabric.network import disconnect_all
from fabric.state import output
from fabric.task_utils import parse_kwargs
from fabric.tasks import WrappedCallableTask, requires_parallel, _execute
from fabric.exceptions import NetworkError
from fabric.utils import abort, warn, error
from fabric.context_managers import settings
from fabric.tasks import execute as fab_execute


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


def mirror_put(local_root, remote_path, validate=True):
    """
    mirror input
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

    if False not in checks:
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
        return fabric_local(capture=True, *args, **kwargs)
    pass


def fabric_execute(task, *args, **kwargs):
    """

    hack for `fabric.execute`. most of the code copy from `fabric.execute`

    Execute ``task`` (callable or name), honoring host/role decorators, etc.

    ``task`` may be an actual callable object, or it may be a registered task
    name, which is used to look up a callable just as if the name had been
    given on the command line (including :ref:`namespaced tasks <namespaces>`,
    e.g. ``"deploy.migrate"``.

    The task will then be executed once per host in its host list, which is
    (again) assembled in the same manner as CLI-specified tasks: drawing from
    :option:`-H`, :ref:`env.hosts <hosts>`, the `~fabric.decorators.hosts` or
    `~fabric.decorators.roles` decorators, and so forth.

    ``host``, ``hosts``, ``role``, ``roles`` and ``exclude_hosts`` kwargs will
    be stripped out of the final call, and used to set the task's host list, as
    if they had been specified on the command line like e.g. ``fab
    taskname:host=hostname``.

    Any other arguments or keyword arguments will be passed verbatim into
    ``task`` (the function itself -- not the ``@task`` decorator wrapping your
    function!) when it is called, so ``execute(mytask, 'arg1',
    kwarg1='value')`` will (once per host) invoke ``mytask('arg1',
    kwarg1='value')``.

    :returns:
        a dictionary mapping host strings to the given task's return value for
        that host's execution run. For example, ``execute(foo, hosts=['a',
        'b'])`` might return ``{'a': None, 'b': 'bar'}`` if ``foo`` returned
        nothing on host `a` but returned ``'bar'`` on host `b`.

        In situations where a task execution fails for a given host but overall
        progress does not abort (such as when :ref:`env.skip_bad_hosts
        <skip-bad-hosts>` is True) the return value for that host will be the
        error object or message.

    .. seealso::
        :ref:`The execute usage docs <execute>`, for an expanded explanation
        and some examples.

    .. versionadded:: 1.3
    .. versionchanged:: 1.4
        Added the return value mapping; previously this function had no defined
        return value.
    """
    my_env = {'clean_revert': True}
    results = {}

    dunder_name = getattr(task, '__name__', None)
    my_env['command'] = getattr(task, 'name', dunder_name)

    task = WrappedCallableTask(task)

    # Filter out hosts/roles kwargs
    new_kwargs, hosts, roles, exclude_hosts = parse_kwargs(kwargs)
    # Set up host list
    my_env['all_hosts'], my_env['effective_roles'] = task.get_hosts_and_effective_roles(hosts, roles,
                                                                                        exclude_hosts, env)

    parallel = requires_parallel(task)

    if parallel:
        # Import multiprocessing if needed, erroring out usefully
        # if it can't.
        try:
            import multiprocessing
        except ImportError:
            import traceback
            tb = traceback.format_exc()
            abort(tb + """
    At least one task needs to be run in parallel, but the
    multiprocessing module cannot be imported (see above
    traceback.) Please make sure the module is installed
    or that the above ImportError is fixed.""")
    else:
        multiprocessing = None

    # Get pool size for this task
    pool_size = task.get_pool_size(my_env['all_hosts'], env.pool_size)
    # Set up job queue in case parallel is needed
    queue = multiprocessing.Queue() if parallel else None
    jobs = JobQueue(pool_size, queue)
    if output.debug:
        jobs._debug = True

    # Call on host list
    if my_env['all_hosts']:
        # Attempt to cycle on hosts, skipping if needed
        for host in my_env['all_hosts']:
            try:
                results[host] = _execute(
                        task, host, my_env, args, new_kwargs, jobs, queue,
                        multiprocessing
                )
            except NetworkError, e:
                results[host] = e
                # Backwards compat test re: whether to use an exception or
                # abort
                if not env.use_exceptions_for['network']:
                    func = warn if env.skip_bad_hosts else abort
                    error(e.message, func=func, exception=e.wrapped)
                else:
                    raise

            # If requested, clear out connections here and not just at the end.
            if env.eagerly_disconnect:
                disconnect_all()

        # If running in parallel, block until job queue is emptied
        if jobs:
            err = "One or more hosts failed while executing task '%s'" % (
                my_env['command']
            )
            jobs.close()
            # Abort if any children did not exit cleanly (fail-fast).
            # This prevents Fabric from continuing on to any other tasks.
            # Otherwise, pull in results from the child run.
            ran_jobs = jobs.run()
            for name, d in ran_jobs.iteritems():
                if d['exit_code'] != 0:
                    if isinstance(d['results'], NetworkError) and \
                            _is_network_error_ignored():
                        error(d['results'].message, func=warn, exception=d['results'].wrapped)
                    elif isinstance(d['results'], BaseException):
                        error(err, exception=d['results'])
                    else:
                        error(err)
                results[name] = d['results']

    # Or just run once for local-only
    else:
        with settings(**my_env):
            results['<local-only>'] = task.run(*args, **new_kwargs)
    # Return what we can from the inner task executions

    return results


def execute(commands):
    try:
        commands_to_run = [(v, [], {}, [], [], []) for v in commands]

        for name, args, kwargs, arg_hosts, arg_roles, arg_exclude_hosts in commands_to_run:
            fab_execute(name, hosts=arg_hosts, roles=arg_roles, exclude_hosts=arg_exclude_hosts, *args, **kwargs)
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
    pass


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
