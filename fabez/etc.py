# -*- coding: utf-8 -*-


from fabric.api import *


def config_nginx(local_name, remote_name=None):
    """
    directory must be ./config/nginx/*.conf
    """

    if remote_name is None:
        remote_name = local_name

    put('./config/nginx/{}.conf /etc/nginx/conf.d/{}.conf'.format(local_name, remote_name))


def config_supervisor(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    put('./config/supervisord/{}.ini /etc/supervisor.d/{}.ini'.format(local_name, remote_name))



