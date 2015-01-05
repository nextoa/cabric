# -*- coding: utf-8 -*-

from fabric.api import *
from fabez.env import *
from fabez.cmd import *
from fabez.server import *
from fabez.io import io_airlog,rm_io_airlog


from fabez.docs import *


import os

def ez(curr):
    routes = {
        'dev':os.path.dirname(__file__)+'/config/dev.conf',
        'ol':os.path.dirname(__file__)+'/config/production.conf',
    }

    bind_hosts(curr,routes)
    pass


def install():
    print "current environment is %s" % ez_env.group
    server_nginx(user='nobody',worker_processes=1,worker_connections=100,old_user='root')
    pass


def stop():
    run('service nginx stop')
    pass


def start():
    run('service nginx start')
    pass


def hello():
    cmd_su('rm /tmp/a','webuser')
    run('rm /tmp/a')
    pass


def fastfs():
    io_airlog()
    pass


def drop_fastfs():
    rm_io_airlog()
    pass


def upgrade():

    if ez_env.group == 'ol':
        cmd_git('/tmp/web-master','https://github.com/kbonez/fabezweb.git',user='webuser')
        pass
    else:
        cmd_git('/tmp/web-dev','https://github.com/kbonez/fabezweb.git',branch='dev')
        pass

    pass


def docs(server=False):
    docs_bootstrap(server)
    pass
