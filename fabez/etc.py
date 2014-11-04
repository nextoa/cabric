# -*- coding: utf-8 -*-


from fabric.api import *

def config_nginx(deploy_root):
    '''
    directory must be project_root/config/nginx/*.conf
    :param path: local path
    '''
    run('cp -rf {}/config/nginx/*.conf /etc/nginx/conf.d/'.format(deploy_root))

def config_supervisor(deploy_root):
    '''
    directory must be project_root/config/supervisor.d/*.ini
    :param path: local path
    '''
    run('cp -rf {}/config/supervisord/*.ini /etc/supervisor.d/'.format(deploy_root))





