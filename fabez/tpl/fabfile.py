# -*- coding: utf-8 -*-

from fabric.api import *
from fabez.env import *

import os


def ez(curr):
    routes = {
        'dev': os.path.dirname(__file__) + '{0}/dev.conf',
        'beta': os.path.dirname(__file__) + '{0}/beta.conf',
        'ol': os.path.dirname(__file__) + '{0}/online.conf',
    }

    bind_hosts(curr, routes)
    pass


def hello_fabric():
    local('echo "You can delete this function after initial it."')
    pass


def upgrade(tag=None, clean=False):
    """
    this function must contain `tag` and `clean` options
    :param tag:
    :param clean:
    :return:
    """

    root = '/tmp/test.fabez.co'  # repo deploy path
    repo = 'https://github.com/mybots/fabez-demo.git'  # repo demo

    if clean:
        run('rm -rf %s' % root)
        pass

    if ez_env.group == 'ol':
        cmd_git(root, repo, branch='master', tag=tag)
        pass
    elif ez_env.group == 'beta':
        cmd_git(root, repo, branch='beta', tag=tag)
        pass
    elif ez_env.group == 'dev':
        cmd_git(root, repo, branch='dev', tag=tag)
        pass
    else:
        print("[warn]:can't find default config,use master.")
        cmd_git(root, repo, branch='master', tag=tag)
        pass

    pass






