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
from user import *

try:
    import pkg_resources  # in package
except:
    pass


def server_nginx(user=None, worker_processes=1, worker_connections=512, old_user='nginx', error_log='/logs/nginx/error.log', access_log='/logs/nginx/access.log'):
    """
    Install Nginx
    :param user: user,default is nobody
    :param worker_processes: process numbers
    :param worker_connections: connections numbers
    :return:None
    """

    cmd_ulimit()

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


def server_redis(card=None, size=None, newer='remi'):
    """
    Install redis server
    @todo support set unixsocket
    @todo support change maxsize
    @todo support change database numbers
    :return:
    """

    utils_remi()
    cmd_ulimit()

    with settings(warn_only=True):
        run('mkdir -p /storage/redis')
        run('useradd redis -r -s /sbin/nologin')

    io_slowlog('redis', 'redis')

    yum_install('redis', newer='remi')

    run('chown redis.redis /storage/redis')
    run('chkconfig --level 35 redis on')

    if card:
        ip = cmd_ip(card)
    else:
        ip = '0.0.0.0'

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


def server_nscd():
    yum_install('nscd')
    run('chkconfig --level 35 nscd on')
    run('service nscd start')
    pass


def server_mongo(card='lo', user='webuser'):
    """
    @note this mongo only support 64-bit system
    :return:
    """
    cmd_ulimit()

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

    io_slowlog('mongo', 'mongod')
    with settings(warn_only=True):
        run('mkdir -p /storage/mongo')
        run('chown -Rf mongod.mongod /storage/mongo')

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


def server_supervisor(user=None, variable=None, pip_path=None, log_dir='/logs/supervisor', log_level='info'):
    """
    Install supervisor
    Default depends pypy
    Focus on tornado

    *note* current, don't use root account
    """

    # yum supervisor id tooooooooooooooooo old
    # run('yum install supervisor -y')

    # try:
    # buf = pkg_resources.resource_string('fabez', 'tpl/supervisord.boot')
    # except:
    # buf = open(os.path.join(os.path.dirname(__file__), 'tpl', 'supervisord.boot')).read()
    # pass
    #
    # with tempfile.NamedTemporaryFile('w', delete=False) as fh:
    # print>> fh, buf
    #
    # put(fh.name, '/etc/init.d/supervisord')
    # os.remove(fh.name)

    # run('chkconfig --level 35 supervisord on')

    # default is python_root



    io_slowlog('supervisor')

    pip('supervisor', pip_path=pip_path)
    # pip('supervisor-logging', pip_path=pip_path)

    if not pip_path:
        python_root = '/usr/local/pypy/bin'

    run('ln -snf {}/supervisord /usr/local/bin/supervisord'.format(python_root))
    run('ln -snf {}/supervisorctl /usr/local/bin/supervisorctl'.format(python_root))

    # with settings(warn_only=True):
    # if run('cat /etc/rc.local | grep "/usr/local/bin/supervisord"').failed:
    #         run('echo "/usr/local/bin/supervisord -c  /etc/supervisord.conf " >> /etc/rc.local')

    with settings(warn_only=True):
        run('mkdir /etc/supervisor.d')
        pass

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/supervisord.conf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'supervisord.conf')).read()
        pass

    buf = template.replace('{$logs}', log_dir) \
        .replace('{$log_level}', log_level)


    replace_variable = 'environment='

    if variable:
        replace_variable = '{},'.format(variable)

    replace_variable += 'PYTHONUNBUFFERED="x"'

    buf = buf.replace('{$variable}', replace_variable)


    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/supervisord.conf')
    os.remove(fh.name)

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/supervisord.start')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'supervisord.start')).read()
        pass

    buf = template

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/init.d/supervisord')
    run('chmod +x /etc/init.d/supervisord')

    os.remove(fh.name)

    run('chkconfig --level 35 supervisord on')

    pass


def server_websuite(user='webuser', python_version='3.4.2', only_pypy=True, pypy_version='2.4', compatible=False):
    run('yum install wget -y')

    server_nscd()
    cmd_useradd(user)
    cmd_ulimit()
    utils_epel()

    utils_git()

    io_webdata(uid=user, gid=user)

    io_slowlog('nginx', user)
    # server_nginx(user)
    server_tengine(user=user)

    io_slowlog('tornado', user)

    # io_slowlog('supervisor', user)
    # server_supervisor()

    server_monit()

    if only_pypy:
        py_pypy(pypy_version)

    else:
        py_python(python_version, compatible=compatible, pypy=pypy_version)

    pip('tornadoez')
    pip('pyjwt')

    utils_imagelib()
    pip_c('pillow')
    pip('pymongo')
    pip('redis')
    pip('pymysql')

    pass


def server_mysql():
    cmd_ulimit()

    with settings(warn_only=True):
        run('rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el6-5.noarch.rpm')

    run('yum install mysql-community-server -y')
    run('chkconfig --level 35 mysqld on')
    pass


def server_tengine(user='webuser', version=None, tornado=True, process=1, connection=1024):
    """
    syslog note
    # need change config use syslog-ng
    # source s_sys {
    #         file ("/proc/kmsg" program_override("kernel: "));
    #         unix-dgram ("/dev/log");
    #         internal();
    #         udp(ip(0.0.0.0) port(514));
    #     };

    # gd-progs use for image-fliter

    :param version:
    :param user:
    :param tornado:
    :return:
    """

    utils_baselib()
    run('yum install jemalloc jemalloc-devel  -y')
    run('yum install GeoIP GeoIP-devel GeoIP-update GeoIP-update6 -y')
    run('yum install pcre-devel openssl-devel nginx -y')

    run('chkconfig --level 35 nginx off')

    if version:
        run('wget http://tengine.taobao.org/download/tengine-{0}.tar.gz -O /tmp/tengine-{0}.tar.gz'.format(version))
    else:
        cmd_git('/tmp/tengine', 'https://github.com/nextoa/tengine.git')

    io_slowlog('nginx', user=user)
    io_aircache('nginx', size=1)

    run('test -d /usr/local/var/lock || mkdir -p /usr/local/var/lock')

    with cd('/tmp'):

        if version:
            run('tar -xvzpf tengine-{0}.tar.gz'.format(version))

        real_path = '/tmp/tengine-{0}'.format(version) if version else '/tmp/tengine'

        with cd(real_path):

            # --without-http_fastcgi_module --without-http_uwsgi_module
            if tornado:
                run('./configure --prefix=/usr/local --user={0} --group={0} --conf-path=/etc/nginx  --sbin-path=/usr/local/sbin '
                    ' --without-http_scgi_module --without-http_memcached_module --without-http_autoindex_module '
                    ' --without-http_auth_basic_module'
                    ' --with-http_spdy_module'
                    ' --with-jemalloc --with-http_spdy_module'
                    ' --with-http_realip_module'
                    ' --with-http_concat_module '

                    # dir path
                    '--pid-path=/usr/local/var/run/nginx.pid --lock-path=/usr/local/var/lock/nginx '

                    # file path
                    ' --http-client-body-temp-path=/aircache/nginx/body_temp'
                    ' --http-proxy-temp-path=/aircache/nginx/proxy_temp'
                    ' --error-log-path=/logs/nginx/error.log --http-log-path=/logs/nginx/access.log'
                    ' --with-syslog'
                    # ' --with-http_reqstat_module'
                    ' --with-http_stub_status_module'
                    ' --with-http_geoip_module'

                    ' --with-http_gzip_static_module'
                    ' --with-http_ssl_module'
                    ' --with-pcre'
                    ' --with-file-aio'

                    # ' --with-http_upstream_keepalive_module'

                    ' --with-http_ssl_module '
                    ' --with-http_footer_filter_module=shared'
                    ' --with-http_sysguard_module=shared'
                    ' --with-http_addition_module=shared'
                    # ' --with-http_xslt_module=shared'
                    # ' --with-http_image_filter_module=shared'
                    ' --with-http_rewrite_module=shared '
                    ' --with-http_sub_module=shared'
                    ' --with-http_flv_module=shared'
                    ' --with-http_slice_module=shared'
                    ' --with-http_mp4_module=shared'
                    ' --with-http_random_index_module=shared'
                    ' --with-http_secure_link_module=shared'
                    ' --with-http_sysguard_module=shared'
                    ' --with-http_charset_filter_module=shared'
                    ' --with-http_userid_filter_module=shared'


                    ' --with-http_footer_filter_module=shared'.format(user))

            else:
                # --without-http_uwsgi_module
                run('./configure --prefix=/usr/local --user={0} --group={0} --conf-path=/etc/nginx  --sbin-path=/usr/local/sbin '
                    ' --without-http_scgi_module --without-http_memcached_module --without-http_autoindex_module '
                    ' --without-http_auth_basic_module'
                    ' --with-http_spdy_module'
                    ' --with-jemalloc --with-http_spdy_module'
                    ' --with-http_realip_module'
                    ' --with-http_concat_module '

                    # dir path
                    '--pid-path=/usr/local/var/run/nginx.pid --lock-path=/usr/local/var/lock/nginx '

                    # file path
                    ' --http-client-body-temp-path=/aircache/nginx/body_temp'
                    ' --http-proxy-temp-path=/aircache/nginx/proxy_temp'
                    ' --error-log-path=/logs/nginx/error.log --http-log-path=/logs/nginx/access.log'
                    ' --with-syslog'
                    # ' --with-http_reqstat_module'
                    ' --with-http_stub_status_module'
                    ' --with-http_geoip_module'

                    ' --with-http_gzip_static_module'
                    ' --with-http_ssl_module'
                    ' --with-pcre'
                    ' --with-file-aio'

                    # ' --with-http_upstream_keepalive_module'

                    ' --with-http_ssl_module '
                    ' --with-http_footer_filter_module=shared'
                    ' --with-http_sysguard_module=shared'
                    ' --with-http_addition_module=shared'
                    # ' --with-http_xslt_module=shared'
                    # ' --with-http_image_filter_module=shared'
                    # ' --with-http_rewrite_module=shared '
                    ' --with-http_sub_module=shared'
                    ' --with-http_flv_module=shared'
                    ' --with-http_slice_module=shared'
                    ' --with-http_mp4_module=shared'
                    ' --with-http_random_index_module=shared'
                    ' --with-http_secure_link_module=shared'
                    ' --with-http_sysguard_module=shared'
                    ' --with-http_charset_filter_module=shared'
                    ' --with-http_userid_filter_module=shared'


                    ' --with-http_footer_filter_module=shared'.format(user))

            run('make')

            with settings(warn_only=True):
                run('service tengine stop')

            run('make install')

            pass

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/nginx.conf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'nginx.conf')).read()
        pass

    buf = template.replace('{$user}', user) \
        .replace('{$process}', str(process)) \
        .replace('{$connection}', str(connection))

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/nginx/nginx.conf')

    os.remove(fh.name)

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/nginx.start')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'nginx.start')).read()
        pass

    buf = template

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/init.d/tengine')

    os.remove(fh.name)

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/nginx.sysconfig')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'nginx.sysconfig')).read()
        pass

    buf = template

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/sysconfig/nginx')

    os.remove(fh.name)

    run('chmod +x  /etc/init.d/tengine')
    run('chkconfig --level 35 tengine on')
    pass


def server_monit(version='5.5-1'):
    # 5.5.1-41
    # run('yum install monit -y')
    # with settings(warn_only=True):
    # run('for i in `rpm -ql monit`;do rm -rf $i; done;')
    # run('rpm -e `rpm -qa | grep -i monit`')

    # with settings(warn_only=True):
    # run('rpm -ivh  https://github.com/nextoa/monit-bin/raw/master/monit-{}.el6.rf.x86_64.rpm'.format(version))
    # run('rpm -Uvh  https://github.com/nextoa/monit-bin/raw/master/monit-{}.el6.rf.x86_64.rpm'.format(version))

    yum_install('monit', 'remi')
    run('chkconfig --level 35 monit on')
    pass


def server_phpd(user='webuser'):
    """
    install php
    :return:
    """
    utils_baselib()
    utils_remi()
    cmd_useradd(user)
    cmd_ulimit()
    utils_git()
    io_webdata(uid=user, gid=user)
    io_slowlog('nginx', user)
    io_slowlog('php-fpm', user)
    server_tengine(user=user, tornado=False)
    server_nscd()

    yum_install('php', newer='remi')
    yum_install('php-fpm', newer='remi')
    yum_install('php-redis', newer='remi')
    yum_install('php-mysql', newer='remi')
    yum_install('php-pecl-yaf', newer='remi')
    yum_install('php-pecl-mongo', newer='remi')
    yum_install('php-pecl-zendopcache', newer='remi')

    run('chkconfig --level 35 php-fpm on')
    pass


def server_nodejs(user='webuser'):
    utils_baselib()
    utils_remi()
    cmd_useradd(user)
    yum_install('nodejs', newer='remi')
    pass


def server_statsd(root, repo='https://github.com/nextoa/statsd.git', user='webuser'):
    # run('pip install graphite')

    utils_baselib()
    classic_git()

    server_nodejs(user)
    io_slowlog('statsd', user)
    cmd_git(root, repo, branch='master', user=user)

    cmd_su('cp {0}/exampleConfig.js {0}/config.js'.format(root))

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/monit-statsd.conf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'monit-statsd.conf')).read()
        pass

    node_path = run('which node')
    buf = template.format(node_path, root, user)


    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/monit.d/statsd.conf')
    os.remove(fh.name)

    pass


# def server_grafana(root,repo='https://github.com/nextoa/grafana.git',user='webuser'):
def server_grafana(root, version='1.9.0', user='webuser'):
    yum_install('wget')
    name = 'grafana-{0}'.format(version)
    run('wget http://grafanarel.s3.amazonaws.com/{0}.tar.gz -O /tmp/{0}.tar.gz'.format(name))

    with cd('/tmp'):
        with settings(warn_only=True):
            run('tar -xvzpf {}.tar.gz'.format(name))
            run('rsync -av /tmp/{}/ {}'.format(name, root))

    # cmd_git(root, repo, branch='master', user=user)

    cmd_su('cp {0}/config.sample.js {0}/config.js'.format(root))
    run('chown -Rf {}.{} {}'.format(user, user, root))

    pass


def server_graphite(user='webuser', port='10002', python='2.6'):
    """
    base on pypy current
    :param version:
    :param python_version:
    :return:
    """
    yum_install('bitmap bitmap-fonts-compat cairo-devel python-whisper python-carbon graphite-web python-memcached memcached')
    run('/usr/bin/python /usr/lib/python{}/site-packages/graphite/manage.py syncdb'.format(python))
    run('chown {0}.{0} /var/lib/graphite-web/graphite.db'.format(user))
    run('chown -Rf {0}.{0} /var/log/graphite-web'.format(user))
    run('chkconfig --level 35 carbon-cache on')
    run('chkconfig --level 35 memcached on')

    # version='1.10.0'):
    # not work well for pypy
    # name = 'py2cairo'
    # wget_install_package(name,version,'http://cairographics.org/releases',suffix='tar.bz2')
    #
    # with cd('/tmp/{}-{}'.format(name,version)):
    # run('/usr/local/pypy/bin/pypy setup.py install')
    # pass

    # # pip('cairocffi')
    # pip('graphite-web')
    # pip('carbon')
    # pip('whisper')
    # pip('django')


    try:
        template = pkg_resources.resource_string('fabez', 'tpl/monit-graphite.conf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'monit-graphite.conf')).read()
        pass

    buf = template.format('/usr/bin/python /usr/lib/python{}/site-packages'.format(python), port, user)

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/monit.d/graphite.conf')
    os.remove(fh.name)

    pass


def server_statsdsuite(user='webuser', monit=None):
    if monit:
        server_monit(monit)

    server_graphite()
    server_statsd('/webdata/statsd', user=user)
    server_grafana('/webdata/grafana', user=user)

    pass


# def server_smtp():
# utils_remi()
# cmd_ulimit()
#
# yum_install('sendmail', newer="remi")
#
# run('chkconfig --level 35 sendmail on')
#
# with settings(warn_only=True):
# run("sed -i -e \"s/^DAEMON_OPTIONS.*dnl/DAEMON_OPTIONS(\\\`Port=smtp,Name=MTA\')dnl/g\" /etc/mail/sendmail.mc")
#
#
# # yum install postfix dovecot
# # yum remove sendmail
#
#
# pass


def server_smtp(host, domain, networks):
    # utils_remi()
    # cmd_ulimit()

    # yum_install('postfix', newer="remi")
    # run('yum remove sendmail -y')



    try:
        template = pkg_resources.resource_string('fabez', 'tpl/postfix.cf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'postfix.cf')).read()
        pass

    buf = template.replace('{$myhostname}', host) \
        .replace('{$mydomain}', domain) \
        .replace('{$mynetworks}', networks)

    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/postfix/main.cf')
    os.remove(fh.name)

    run('chkconfig --level 35 postfix on')

    pass


# restart feature
def restart_web(config=None):
    # supervisor_restart()
    if config:
        config_nginx(config)

    run('service tengine reload')
    run('service tengine restart')


def restart_monit(config=None):

    if config:
        config_monit(config)
        run('service monit restart')

    pass


def reboot_monit(name=None, config=None):
    if config:
        config_monit(config)
        run('service monit restart')

    if name:
        run('monit restart {}'.format(name))
    # run('service monit restart')



def reboot_supervisor(name=None, config=None):
    if config:
        run('service supervisord stop')
        config_supervisor(config)
        run('service supervisord start')

    if name and not config:
        run('supervisorctl restart {}'.format(name))






