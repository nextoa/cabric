# -*- coding: utf-8 -*-


from fabric.api import *

from fabez.env import *

import tempfile


def config_nginx(local_name, remote_name=None):
    """
    directory must be ./config/nginx/*.conf
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/nginx/{}.conf'.format(local_name), '/etc/nginx/conf.d/{}.conf'.format(remote_name))


def config_supervisor(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/supervisord/{}.ini'.format(local_name), '/etc/supervisor.d/{}.ini'.format(remote_name))


def config_monit(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/monit/{}.conf'.format(local_name), '/etc/monit.d/{}.conf'.format(remote_name))


def config_mongo(local_name, *args):
    """
    directory must be ./config/mongo/*.conf
    """

    buf = open('./config/mongo/{}.conf'.format(local_name)).read()

    buff = buf.format(*args)

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buff

    put(fh.name, '/etc/mongod.conf')
    os.remove(fh.name)
    pass


def config_redis(local_name,*args):
    """
    directory must be ./config/redis/*.conf
    """
    buf = open('./config/redis/{}.conf'.format(local_name)).read()

    buff = buf.format(*args)

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buff

    put(fh.name, '/etc/redis.conf')
    os.remove(fh.name)
    pass


def config_php(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/php/{}.ini'.format(local_name), '/etc/php.d/{}.ini'.format(remote_name))


def config_php_fpm(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/php-fpm/{}.conf'.format(local_name), '/etc/php-fpm.d/{}.conf'.format(remote_name))

