# -*- coding: utf-8 -*-

from fabric.api import *
from fabez.cmd import (cmd_git, cmd_ip)


def server_nginx(user=None, worker_processes=16, worker_connections=512, old_user='nginx',error_log='/logs/nginx/error.log',access_log='/logs/nginx/access.log'):
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
    run('sed -i -e "s/\(error_log\s*\)[a-zA-Z\/._0-9]*/\\1%s/g" /etc/nginx/nginx.conf' % error_log.replace('/','\/'))
    run('sed -i -e "s/\(access_log\s*\)[a-zA-Z/._0-9]*/\\1%s/g" /etc/nginx/nginx.conf' % access_log.replace('/','\/'))





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


def server_mongo():
    '''
    @TODO. currently, this is for develop env
    :return:
    '''
    run('yum install mongodb-server -y')
    run('chkconfig --level 35 mongod on')
    pass


def server_gitolite(pubkey=None):
    '''
    @TODO. create gitolite server
    :param pubkey:
    :return:
    '''
    run('mkdir /repo')
    cmd_git('/tmp/gitolite', 'https://github.com/kbonez/gitolite.git')

    if pubkey is None:
        abort("please set your pubkey.")




    # put pub key
    # 执行脚本 @todo 等下次在安装的时候再说

    pass


def server_supervisor(user):
    '''
    Install supervisor
    '''
    # with settings(warn_only=True):
    # run('pip install supervisor')
    #     if run('test -d /usr/local/etc/supervisor.d').failed:
    #         run('mkdir /usr/local/etc/supervisor.d')
    #     run(
    #         "grep '\[supervisord\]' /usr/local/etc/supervisord.conf || echo \"[supervisord]\nuser=%s\nlogfile=/tmp/supervisord.log\nlogfile_maxbytes=50MB\nlogfile_backups=10\nloglevel=info\" >>  /usr/local/etc/supervisord.conf" % user)
    #
    #     run(
    #         "grep '\[unix_http_server\]' /usr/local/etc/supervisord.conf || echo '[unix_http_server]\nfile = /usr/local/var/run/supervisor.sock' >> /usr/local/etc/supervisord.conf")
    #
    #     run(
    #         "grep '\[rpcinterface:supervisor\]' /usr/local/etc/supervisord.conf || echo '[rpcinterface:supervisor]\nsupervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface' >> /usr/local/etc/supervisord.conf")
    #
    #     run(
    #         "grep '\[supervisorctl\]' /usr/local/etc/supervisord.conf || echo \"[supervisorctl]\nserverurl=unix:///usr/local/var/run/supervisor.sock\" >>  /usr/local/etc/supervisord.conf")
    #
    #     run(
    #         "grep '\[include\]' /usr/local/etc/supervisord.conf || echo '[include]\nfiles = supervisor.d/*.ini' >> /usr/local/etc/supervisord.conf")
    #
    #     run(
    #         "grep 'supervisord' /etc/rc.local || echo '/usr/local/bin/supervisord -c /usr/local/etc/supervisord.conf  --pidfile=/usr/local/var/run/supervisord.pid' >> /etc/rc.local")


    run('yum install supervisor -y')
    run('chkconfig --level 35 supervisor on')

    pass


def rm_server_supervisor():
    with settings(warn_only=True):
        run('pip uninstall supervisor -y')
        run('rm -rf /usr/local/etc/supervisor*')
    pass


