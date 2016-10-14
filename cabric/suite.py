# -*- coding: utf-8 -*-

from cabric.utils import utils_epel, utils_git, utils_baselib, utils_human, utils_remi
from cabric.cmd import cmd_ulimit,cmd_useradd
from cabric.io import io_webdata
from cabric.server import server_tengine, server_nginx, server_syslog, server_nscd, server_supervisor
from cabric.pythonic import py_python, py_pypy


def suite_base(network=True, epel=True, remi=True, deploy=True, baselib=True, human_tools=True):
    cmd_ulimit()

    # improve network feature
    if network:
        server_nscd()
        pass

    # for epel repo
    if epel:
        utils_epel()
        pass

    if remi:
        utils_remi()

    if deploy:
        utils_git()

    if baselib:
        utils_baselib()

    if human_tools:
        utils_human()

    pass


def suite_webserver(user='webuser', pypy='2.4', python='3.4.2', php=None, nginx=True, tengine=False, syslog=True):
    """
    create webserver
    :param user:
    :param pypy:
        - install supervisor
    :param python:
    :param nginx:
    :param tengine:
    :param syslog:
    :return:
    """


    #@todo recode
    if pypy == 'None':
        pypy = None

    if python == 'None':
        python = None


    cmd_useradd(user)
    io_webdata(uid=user, gid=user)


    suite_base()

    if tengine:
        server_tengine(user=user)

    if nginx:
        server_nginx(user=user)


    if tengine or nginx:
        io_slowlog('nginx', user)
        pass


    if tengine and nginx:
        raise Exception("can't use tengine and nginx same time")

    if pypy and python:
        py_python(python, compatible=True, pypy=pypy)
    elif pypy:
        py_pypy(pypy=pypy)
    else:
        py_python(python, compatible=False, pypy=None)
        pass

    if pypy:
        server_supervisor()

    if php:
        server_phpd(user=user)

    if syslog:
        server_syslog()
        pass

    pass


