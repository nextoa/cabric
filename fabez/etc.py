# -*- coding: utf-8 -*-


from fabric.api import *

from fabez.env import *


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



