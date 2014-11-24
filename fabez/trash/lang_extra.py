# -*- coding: utf-8 -*-


from fabric.api import *
from fabez.cmd import *
import os

import tempfile

try:
    import pkg_resources
except:
    pass

# @deprecated


def lang_extra_pecl_install(php_package):
    """
    @deprecated drop PHP
    php pecl tools
    :param php_pkg:
    :return:
    """
    run("yes '' | /usr/local/bin/pecl install -f {}".format(php_package))
    pass



def lang_extra_pecl_manual(php_package,repo,tag=None):
    """
    @deprecated drop PHP

    php pecl manual install tools
    :param php_pkg:
    :return:
    """

    local_path = '/tmp/'+php_package
    cmd_git(local_path,repo,tag=tag)

    with cd(local_path):
        run('/usr/local/bin/phpize ')
        run('./configure --with-php-config=/usr/local/bin/php-config')
        run('make && make install')
        pass


    #@todo add file append feature

    pass





def lang_extra_php_yaf(server_name, environ='product', root=None, more_domain='', log_dir='/logs/nginx'):
    """
    @deprecated  drop PHP

    install yaf config for nginx
    :return:
    """

    if root is None:
        root = server_name

    try:
        template = pkg_resources.resource_string('fabez', 'tpl/yaf.conf')
    except:
        template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'yaf.conf')).read()
        pass

    buf = template.replace('{$root}', root) \
        .replace('{$yaf_environ}', environ) \
        .replace('{$log}', log_dir) \
        .replace('{$localhost}', server_name) \
        .replace('{$server_names}', server_name+ ' {}'.format(more_domain))

    remote_path = '/etc/nginx/conf.d/%s.conf' % server_name


    with tempfile.NamedTemporaryFile('w',delete=False) as fh:
        print>> fh, buf


    put(fh.name, remote_path)
    os.remove(fh.name)


    with cd('/usr/local'):
        with settings(warn_only=True):
            if run('grep ^yaf.environ ./etc/php.d/yaf.ini').failed:
                run('echo "yaf.environ = %s" >> ./etc/php.d/yaf.ini ' % environ)
            else:
                run('sed -i -e "s/^\(yaf.environ\s*=\s*\).*/\\1%s/g" ./etc/php.d/yaf.ini' % environ)


    pass







