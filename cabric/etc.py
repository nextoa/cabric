# -*- coding: utf-8 -*-


from fabric.api import *

from cabric.env import *

import tempfile


def config_nginx(local_name, remote_name=None):
    """
    directory must be ./config/nginx/*.conf
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/nginx/{}.conf'.format(local_name), '/etc/nginx/conf.d/{}.conf'.format(remote_name))


def config_supervisor(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/supervisord/{}.ini'.format(local_name), '/etc/supervisor.d/{}.ini'.format(remote_name))


def config_monit(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/monit/{}.conf'.format(local_name), '/etc/monit.d/{}.conf'.format(remote_name))


def config_squid(local_name='squid', remote_name='squid'):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/squid/{}.conf'.format(local_name), '/etc/squid/{}.conf'.format(remote_name))


def config_mongo(local_name, *args):
    """
    directory must be ./config/mongo/*.conf
    """

    buf = open('./config/mongo/{}.conf'.format(local_name)).read()

    buff = buf.format(*args)

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print >> fh, buff

    put(fh.name, '/etc/mongod.conf')
    os.remove(fh.name)
    pass


def config_redis(local_name, *args):
    """
    directory must be ./config/redis/*.conf
    """
    buf = open('./config/redis/{}.conf'.format(local_name)).read()

    buff = buf.format(*args)

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print >> fh, buff

    put(fh.name, '/etc/redis.conf')
    os.remove(fh.name)
    pass


def config_php(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/php/{}.ini'.format(local_name), '/etc/php.d/{}.ini'.format(remote_name))


def config_php_fpm(local_name, remote_name=None):
    """
    directory must be ./config/supervisor.d/*.ini
    """

    if remote_name is None:
        remote_name = local_name

    if ez_env.group != 'ol':
        local_name += '_' + ez_env.group

    put('./config/php-fpm/{}.conf'.format(local_name), '/etc/php-fpm.d/{}.conf'.format(remote_name))


def config_graphite(local_name, *args):
    """
    directory must be ./config/graphite-web/*.conf
    """

    buf = open('./config/graphite-web/{}.py'.format(local_name)).read()
    buff = buf

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print >> fh, buff

    put(fh.name, '/etc/graphite-web/local_settings.py')
    os.remove(fh.name)
    pass


def config_carbon(local_name, *args):
    """
    directory must be ./config/carbon/*.conf
    """

    buf = open('./config/carbon/{}.conf'.format(local_name)).read()
    buff = buf

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print >> fh, buff

    put(fh.name, '/etc/carbon/storage-schemas.conf')
    os.remove(fh.name)

    pass


def config_statsd(local_name, root='/webdata/statsd', *args):
    """
    directory must be ./config/statsd/*.conf
    """

    buf = open('./config/statsd/{}.js'.format(local_name)).read()
    # buff = buf.format(*args)
    buff = buf

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print >> fh, buff

    put(fh.name, '{}/config.js'.format(root))
    os.remove(fh.name)

    pass


def config_grafana(local_name, root='/webdata/grafana', *args):
    """
    directory must be ./config/grafana/*.conf
    """

    buf = open('./config/grafana/{}.js'.format(local_name)).read()
    buff = buf

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print >> fh, buff

    put(fh.name, '{}/config.js'.format(root))
    os.remove(fh.name)

    put('./config/grafana/{}.json'.format(local_name), '{}/app/dashboards/default.json'.format(root))

    pass


def config_mongos(*args):
    if len(args) < 1:
        raise "you must at least set one configdb."

    try:
        buf = pkg_resources.resource_string('cabric', 'tpl/mongos.start')
    except:
        buf = open(os.path.join(os.path.dirname(__file__), 'tpl', 'mongos.start')).read()
        pass

    user='root'
    buf = buf.replace('{routers}', ','.join(args)).replace('{user}', user)

    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print >> fh, buf

    put(fh.name, '/etc/init.d/mongos')
    os.remove(fh.name)

    run('chkconfig --level 35 mongos on')
    run('chmod +x /etc/init.d/mongos')
    run('service mongos restart')

    pass
