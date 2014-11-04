# -*- coding: utf-8 -*-

import tempfile

from fabric.api import *

from fabez.cmd import *
from server import *
from io import *
from perm import *
from utils import *
from pythonic import *
from etc import *


try:
    import pkg_resources  # in package
except:
    pass


def server_nginx(user=None, worker_processes=16, worker_connections=512, old_user='nginx', error_log='/logs/nginx/error.log', access_log='/logs/nginx/access.log'):
    """
    Install Nginx
    :param user: user,default is nobody
    :param worker_processes: process numbers
    :param worker_connections: connections numbers
    :return:None
    """

    run('yum install nginx -y')

    run('chkconfig --level 35 nginx on')

    # custom config
    if user:
        run('sed -i -e "s/\(user\s*\)%s/\\1%s/g" /etc/nginx/nginx.conf' % (old_user, user))
    run('sed -i -e "s/\(worker_processes\s*\)[0-9]*/\\1%d/g" /etc/nginx/nginx.conf' % worker_processes)
    run('sed -i -e "s/\(worker_connections\s*\)[a-zA-Z\/._0-9]*/\\1%d/g" /etc/nginx/nginx.conf' % worker_connections)
    run('sed -i -e "s/\(error_log\s*\)[a-zA-Z\/._0-9]*/\\1%s/g" /etc/nginx/nginx.conf' % error_log.replace('/', '\/'))
    run('sed -i -e "s/\(access_log\s*\)[a-zA-Z/._0-9]*/\\1%s/g" /etc/nginx/nginx.conf' % access_log.replace('/', '\/'))


def rm_server_nginx():
    """
    unintall nginx
    :return:
    """

    with settings(warn_only=True):
        run('chkconfig --level 35 nginx off')
        run('yum erase nginx -y')
        run('rm -rf /etc/nginx')

    pass


def server_redis(card='eth0', size=None):
    """
    Install redis server
    @todo support set unixsocket
    @todo support change maxsize
    @todo support change database numbers
    :return:
    """
    with settings(warn_only=True):
        run('mkdir -p /storage/redis')

    run('yum install redis -y')
    run('chown redis.redis /storage/redis')
    run('chkconfig --level 35 redis on')

    ip = cmd_ip(card)
    run('sed -i -e "s/\(bind\s*\)[0-9\.]*/\\1%s/g" /etc/redis.conf' % ip)

    # if size:
    # run('sed -i -e "s/\(^maxmemory \s*\)[0-9\.]*/\\1%s/g" /etc/redis.conf' % ip)


    pass


def rm_server_redis(clean=False):
    """
    Remove redis server
    :param clean:
    :return:
    """
    run('yum earse redis -y')

    if clean is True:
        run('rm -rf /storage/redis')

    pass


def server_mongo(card='lo'):
    """
    @note this mongo only support 64-bit system
    :return:
    """

    try:
        buf = pkg_resources.resource_string('fabez', 'tpl/mongodb.repo')
    except:
        buf = open(os.path.join(os.path.dirname(__file__), 'tpl', 'mongodb.repo')).read()
        pass

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/yum.repos.d/mongodb.repo')
    os.remove(fh.name)

    run('yum install mongodb-org -y')

    if card:
        ip = cmd_ip(card)
        run('sed -i -e "s/\(bind_ip\s*=\s*\)[0-9\.]*/\\1%s/g" /etc/mongod.conf' % ip)

    run('chkconfig --level 35 mongod on')
    pass


def server_gitolite(pubkey=None):
    '''
    @TODO. create gitolite server
    :param pubkey:
    :return:
    '''
    run('yum install gitolite3 -y')
    if pubkey is None:
        run('cp ~/.ssh/authorized_keys /tmp/gitolite.pub')
    else:
        put_public_key(pubkey, '/tmp/gitolite.pub')

    run('chown gitolite3 /tmp/gitolite.pub')
    cmd_su('gitolite setup -pk /tmp/gitolite.pub', 'gitolite3')

    pass


def server_supervisor(user='webuser', tmp='/tmp', log_dir='/logs/supervisor', log_level='info'):
    """
    Install supervisor
    """

    # yum supervisor id tooooooooooooooooo old
    # run('yum install supervisor -y')

    # try:
    #     buf = pkg_resources.resource_string('fabez', 'tpl/supervisord.boot')
    # except:
    #     buf = open(os.path.join(os.path.dirname(__file__), 'tpl', 'supervisord.boot')).read()
    #     pass
    #
    # with tempfile.NamedTemporaryFile('w', delete=False) as fh:
    #     print>> fh, buf
    #
    # put(fh.name, '/etc/init.d/supervisord')
    # os.remove(fh.name)

    # run('chkconfig --level 35 supervisord on')


    with settings(warn_only=True):
        if run('cat /etc/rc.local | grep "/usr/local/bin/supervisord"').failed:
            run('echo "/usr/local/bin/supervisord" >> /etc/rc.local')

    with settings(warn_only=True):
        run('test -d /etc/supervisor.d || mkdir /etc/supervisor.d')

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/supervisord.conf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'supervisord.conf')).read()
        pass

    buf = template.replace('{$username}', user) \
        .replace('{$tmp}', tmp) \
        .replace('{$logs}', log_dir) \
        .replace('{$log_level}', log_level)


    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/supervisord.conf')
    os.remove(fh.name)

    pass


def server_websuite(user='webuser', python_version='3.4.2'):
    run('yum install wget -y')

    cmd_useradd(user)
    cmd_ulimit()
    utils_epel()

    utils_git()

    io_webdata(uid=user, gid=user)

    io_slowlog('nginx', user)
    server_nginx(user)

    io_slowlog('supervisor', user)
    server_supervisor()

    py_python(python_version)

    pip('tornadoez')
    pip('pyjwt')
    pip('pillow')
    pip('pymongo')
    pip('redis')
    pip('pymysql')

    pass


def server_mysql():
    with settings(warn_only=True):
        run('rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el6-5.noarch.rpm')

    run('yum install mysql-community-server -y')
    run('chkconfig --level 35 mysqld on')
    pass


