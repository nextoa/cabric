# -*- coding: utf-8 -*-

from fabric.api import *
from fabez.env import *
from fabez.cmd import *
from fabez.server import *
from fabez.api import *





import os

def ez(curr):
    routes = {
        'dev':os.path.dirname(__file__)+'/config/fabez/dev.conf',
        'test':os.path.dirname(__file__)+'/config/fabez/test.conf',
        'ol':os.path.dirname(__file__)+'/config/fabez/online.conf',
    }

    bind_hosts(curr,routes)
    pass


def fabez_debug():
    local('echo "This message is from ."')
    pass



def upload_server_key():
    """
    上传私钥key
    :return:
    """
    put_private_key('~/.ssh/baixing/id_weekweekup','webuser')
    pass



def upgrade(tag=None,clean=False,depend=False):
    """
    执行升级
    :return:
    """

    root = '/webdata/fabez.ez.co'
    repo = 'gitolite3@fabez.kbonez.com:fabez.git'

    if clean:
        run('rm -rf %s' % root)
        pass



    if ez_env.group == 'ol':
        cmd_git(root, repo, branch='master', user='webuser',tag=tag)
        pass
    elif ez_env.group == 'test':
        cmd_git(root, repo, branch='beta', user='webuser',tag=tag)
        pass
    elif ez_env.group == 'dev':
        cmd_git(root, repo, branch='dev', user='webuser',tag=tag)
        pass
    else:
        print "找不到指定的配置环境,SKIP"
        pass

    if depend:
        run('cd /webdata/fabez.ez.co && python setup.py install')
        run('chown -Rf webuser.webuser /webdata/fabez.ez.co')


    pass




