# -*- coding: utf-8 -*-



from fabric.api import *


def putc_nginx(path):
    '''
    put nginx config file
    :param path: local path
    '''
    remote_path = '/etc/nginx/conf.d/'
    put(path, remote_path)



