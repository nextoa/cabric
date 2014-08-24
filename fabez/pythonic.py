# -*- coding: utf-8 -*-



import os
from fabric.api import *
from fabez.utils import (utils_baselib)
from fabez.cmd import (cmd_git)


def py_setuptools():


    pass



def py_setup_py(code_dir=None, python='python'):
    '''
    short for cd path && python setup.py install
    :param code_dir: path
    :param python: python path,default is python
    '''
    with cd(code_dir):
        run('%s setup.py install' % python)


def rm_py_setup_py(code_dir=None,python='python'):
    '''
    @TODO uninstall package install manual
    :param code_dir:user dir
    :param python:python
    '''
    # with cd(code_dir):
    #     run('%s setup.py uninstall' % python)
    abort("please use uninstall_pip to remove package")
    pass










def uninstall_python():
    with settings(warn_only=True):
        uninstall_pip('setuptools')
        run('rm -rf /usr/local/bin/pip*')
        run('rm -rf /usr/local/bin/python*')
        run('rm -rf /usr/local/*/python*')
        run('rm -rf /usr/local/etc/supervisor*')
        run('rm -rf /tmp/python')
        run('rm -rf /tmp/pip')
        run('rm -rf /tmp/setuptools')
    pass



def pip(package=None, upgrade=None):
    '''
    install package use pip
    :param package: package name
    :param upgrade: true
    '''
    if package:
        run('pip install %s' % package)
        if upgrade:
            run('pip install %s --upgrade' % package)


def uninstall_pip(package):
    '''
    uninstall package from pip
    :param package:
    :return:
    '''
    with settings(warn_only=True):
        run('pip uninstall %s -y' % package)



def tornado(ez=None):
    '''
    install tornado
    :param ez:
    :return:
    '''
    if ez:
        pip('tornadoez', True)
    else:
        pip('tornado', True)


def putc_supervisor(path):
    '''
    put supervisor config file
    :param path: local path
    '''
    remote_path = '/usr/local/etc/supervisor.d/'
    put(path, remote_path)

    pass