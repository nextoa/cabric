# -*- coding: utf-8 -*-

from fabric.api import *
from fabez.env import *

import os

def ez(curr):
    routes = {
        'dev':os.path.dirname(__file__)+'{0}/dev.conf',
        'test':os.path.dirname(__file__)+'{0}/test.conf',
        'ol':os.path.dirname(__file__)+'{0}/online.conf',
    }

    bind_hosts(curr,routes)
    pass


def fabez_debug():
    local('echo "You can delete this function after initial it."')
    pass




def upgrade(tag=None, clean=False):
    """
    this function must contain `tag` and `clean` options
    :param tag:
    :param clean:
    :return:
    """

    root = '/tmp/test.fabez.co'     #repo deploy path
    repo = 'https://github.com/mybots/fabez-demo.git' # repo demo

    if clean:
        run('rm -rf %s' % root)
        pass

    if ez_env.group == 'ol':
        cmd_git(root, repo, branch='master',tag=tag)
        pass
    elif ez_env.group == 'test':
        cmd_git(root, repo, branch='beta', tag=tag)
        pass
    elif ez_env.group == 'dev':
        cmd_git(root, repo, branch='dev', tag=tag)
        pass
    else:
        print "找不到指定的配置环境,使用默认"
        cmd_git(root, repo, branch='master', user='webuser', tag=tag)
        pass

    run('cp /webdata/fabez.baixing.com/projects/fabez-bx/config/supervisord/supervisord.conf /usr/local/etc/')
    run('cp /webdata/fabez.baixing.com/projects/fabez-bx/config/supervisord/conf.d/* /usr/local/etc/supervisor.d/')
    run('cp -rf /webdata/fabez.baixing.com/projects/fabez-bx/config/nginx/ssl.conf  /etc/nginx/conf.d/')

    pass



    pass

