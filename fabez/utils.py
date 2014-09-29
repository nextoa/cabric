# -*- coding: utf-8 -*-

from fabric.api import *


def utils_git(proxy=None):
    '''
    Install git
    :param proxy:proxy server
    :return:
    '''
    run('yum install git -y')

    if proxy:
        run('git config --global http.proxy {}'.format(proxy))

    pass



def rm_utils_git():
    '''
    remove git and git config
    :return:
    '''
    with settings(warn_only=True):
        run('yum erase git -y')
        run('rm -rf ~/.gitconfig')





def utils_baselib():
    '''
    install base package
    :return:
    '''
    run(
        'yum install gcc-c++ make zlib-devel libxml2  libxml2-devel  bzip2-libs bzip2-devel  libcurl-devel  libjpeg libjpeg-devel  libpng libpng-devel  freetype freetype-devel  libmcrypt libmcrypt-devel  libtool-ltdl libtool-ltdl-devel openssl-devel autoconf re2c bison pcre_devel pcre -y')
    run('mkdir -p /usr/local/var/run')
    pass





def utils_epel():
    """
    install epel lib
    :return:
    """
    with settings(warn_only=True):
        run('rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm')
    pass


