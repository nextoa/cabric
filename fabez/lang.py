# -*- coding: utf-8 -*-


from fabric.api import *
from fabez.utils import utils_baselib
from fabez.cmd import cmd_git
from fabez.io import *
from fabez.env import ez_env
from fabez.lang_extra import *
from fabez.pythonic import *



def lang_python(tag=None):
    '''
    install python. include python,setuptools,pip and supervisord
    :param pip_index_url:proxy url
    '''

    utils_baselib()
    cmd_git('/tmp/python', 'https://github.com/kbonez/python.git', tag=None)


    with cd('/tmp/python'):
        run('./configure')
        run('make && make install')
        py_pip()
        pip('Sphinx')
    pass



def lang_php(branch='master', user='webuser', repo='https://github.com/kbonez/php-src.git', tag=None,
             logs='/logs/php-fpm'):
    """
    for php, will bind php-fpm
    :param branch:
    :param user:
    :param repo:
    :param tag:
    :return:
    """

    cmd_git('/tmp/php', repo, branch=branch, tag=tag)

    with cd('/tmp/php'):
        if tag is None:
            run('./buildconf')
        else:
            run('./buildconf --force')

        # '--enable-embedded-mysqli'
        run(
            "./configure '--prefix=/usr/local' '--enable-fpm' '--enable-pcntl' '--enable-opcache' '--enable-mbstring' '--enable-sockets' '--with-mysql=mysqlnd'  '--with-mysqli=mysqlnd'  '--enable-mysqlnd' '--with-pdo-mysql=mysqlnd' '--with-iconv' '--with-freetype-dir' '--with-jpeg-dir' '--with-png-dir' '--with-zlib' '--with-libxml-dir=/usr' '--enable-xml' '--disable-rpath'  '--enable-bcmath' '--enable-shmop' '--enable-sysvsem' '--enable-inline-optimization' '--with-curl' '--with-curlwrappers' '--enable-mbregex' '--enable-mbstring' '--with-mcrypt' '--with-gd' '--enable-gd-native-ttf' '--with-openssl' '--with-mhash' '--enable-pcntl' '--enable-sockets' '--with-xmlrpc' '--enable-zip' '--enable-ftp' '--enable-soap' '--enable-json' '--with-bz2' '--disable-ipv6' '--with-gettext' '--enable-fpm' '--with-fpm-user={0}' '--with-fpm-group={0}' '--with-config-file-path=/usr/local/etc' '--with-config-file-scan-dir=/usr/local/etc/php.d'  ".format(
                user))
        run("make && make install")

    io_socks('php-fpm', user=user)



    # config php-fpm
    with cd('/usr/local'):
        with settings(warn_only=True):
            if run('test -f ./etc/php-fpm.conf').failed:
                run('cp ./etc/php-fpm.conf.default ./etc/php-fpm.conf')

            if run('test -d ./etc/php.d').failed:
                run('mkdir ./etc/php.d')

            if run('test -f ./etc/php.ini').failed:
                run('touch ./etc/php.ini')

        # change php-var directory permission
        run('chown -Rf %s.%s /usr/local/var' % (user, user))

        # php-fpm sock
        run('sed -i -e "s/\(listen\s*=\s*\).*/\\1%s/g" ./etc/php-fpm.conf' % '/usr/local/var/run/php-fpm/php-fpm.sock'.replace('/', '\/'))


        # set php-fpm sock user
        with settings(warn_only=True):
            if run('grep "^listen.owner" ./etc/php-fpm.conf').failed:
                run('sed -i -e "s/;\(listen\.owner\s*=\s*\).*/\\1%s/g" ./etc/php-fpm.conf' % user)
            else:
                run('sed -i -e "s/\(listen\.owner\s*=\s*\).*/\\1%s/g" ./etc/php-fpm.conf' % user)

        with settings(warn_only=True):
            if run('grep "^listen.group" ./etc/php-fpm.conf').failed:
                run('sed -i -e "s/;\(listen\.group\s*=\s*\).*/\\1%s/g" ./etc/php-fpm.conf' % user)
            else:
                run('sed -i -e "s/\(listen\.group\s*=\s*\).*/\\1%s/g" ./etc/php-fpm.conf' % user)


        # # php-fpm log
        # fpm_error_log = logs + '/error.log'
        #
        # with settings(warn_only=True):
        #     if run('grep ^error_log ./etc/php-fpm.conf').failed:
        #         run('sed -i -e "s/^;\(error_log\s*=\s*\).*/\\1%s/g" ./etc/php-fpm.conf' % fpm_error_log.replace('/', '\/'))
        #     else:
        #         run('sed -i -e "s/^\(error_log\s*=\s*\).*/\\1%s/g" ./etc/php-fpm.conf' % fpm_error_log.replace('/', '\/'))
        #         pass


        # config pecl
        run('./bin/pear config-set php_ini /usr/local/etc/php.ini')
        run('./bin/pecl config-set php_ini /usr/local/etc/php.ini')

        # install xdebug
        if ez_env.group[0:3] == 'dev' or ez_env.group[0:4] == 'test':
            lang_extra_pecl_install('xdebug')

            with settings(warn_only=True):
                if run('test -f ./etc/php.d/xdebug.ini').failed:
                    run(
                        'echo "xdebug.remote_enable = on\nxdebug.remote_connect_back = on\nxdebug.idekey = \"vagrant\"\n" > ./etc/php.d/xdebug.ini')

            pass


    # install xhprof
    lang_extra_pecl_install('xhprof')



    # config php-fpm service
    with settings(warn_only=True):
        if run("grep '^/usr/local/sbin/php-fpm' /etc/rc.local").failed:
            run('echo "/usr/local/sbin/php-fpm" >> /etc/rc.local')

    pass
