# -*- coding: utf-8 -*-

from fabric.api import *
import os
import pkg_resources
import tempfile


def cmd_userexist(user):
    """
    check user exist or not
    :param user:
    :return:
    """

    with settings(warn_only=True):
        if run('cat /etc/passwd | grep ^%s' % user).failed:
            return False
        else:
            return True

    pass


def cmd_useradd(user, shell='`which bash`', extra=[], **kwargs):
    """
    Remote UserAdd
    :param user: username
    :param extra: extra
    :return:
    """

    if cmd_userexist(user) is False:
        run('useradd %s -d /home/%s -s %s ' % (user, user, shell))

        with settings(warn_only=True):
            run('mkdir /home/%s && chown %s.%s /home/%s' % (user, user, user, user))
            for dir in extra:
                if run("test -d %s" % dir).failed:
                    run('mkdir %s' % dir)
                run('chown -Rf %s.%s %s' % (user, user, dir))

    pass


def cmd_userdel(user, clean=True, extra=[]):
    """
    clean user files
    :param user:
    :param clean:
    :param extra:
    :return:
    """

    if cmd_userexist(user) is False:
        raise "User %s not exits" % user

    if clean is True:
        run('userdel -r %s' % user)
    else:
        run('userdel  %s' % user)

    with settings(warn_only=True):
        for dir in extra:
            run("rm -rf  %s" % dir)

    pass


def cmd_ulimit(limit=65535):
    """
    set all ulimit to number
    :return:
    """

    try:
        buf = pkg_resources.resource_string('fabez', 'tpl/90-nproc.conf')
    except:
        buf = open(os.path.join(os.path.dirname(__file__), 'tpl', '90-nproc.conf')).read()
        pass


    # only support python2.x
    with tempfile.NamedTemporaryFile('w', delete=False) as fh:
        print>> fh, buf

    put(fh.name, '/etc/security/limits.d/90-nproc.conf')
    os.remove(fh.name)


def cmd_expanduser(user=None):
    '''
    get userpath prefix ~ from remote server. for example: ~webuser
    :param user: username on remote
    '''
    if user is None:
        return '~'

    with settings(warn_only=True):
        if run('cat /etc/passwd | grep %s' % user).failed:
            abort("User:%s not exits" % user)
        else:
            user_path = run("cat /etc/passwd | grep %s | awk -F ':' '{print $6}'" % user)

    return user_path


def cmd_bind_host(ip=None, name=None):
    '''
    bind ip-name to /etc/hosts
    :param ip:ip address
    :param name: domain name
    '''
    with settings(warn_only=True):
        match = '%s %s' % (ip, name)
        if run('grep "%s" /etc/hosts' % match).failed:
            run('echo "%s" >> /etc/hosts' % match)

    pass


def rm_cmd_bind_host(ip=None, name=None):
    '''
    clean user bind ip-host
    :return:
    '''
    with settings(warn_only=True):
        match = '%s %s' % (ip, name)
        if run('grep "%s" /etc/hosts' % match):
            run('sed -i -e "s/%s//g" /etc/hosts' % match)

    pass


def cmd_known_host(name, user=None):
    '''
    set ssh figerprint
    :param name:domain
    :param user:webuser
    '''

    user_path = cmd_expanduser(user)
    command0 = 'grep %s %s/.ssh/known_hosts' % (name, user_path)
    command1 = 'ssh-keyscan %s >> %s/.ssh/known_hosts' % (name, user_path)
    command2 = 'sed -i -e "s/%s//g" %s/.ssh/known_hosts' % (name, user_path)

    if user:
        command0 = 'su - %s -c "%s"' % (user, command0)
        command1 = 'su - %s -c "%s"' % (user, command1)
        command2 = 'su - %s -c "%s"' % (user, command2)
        pass

    with settings(warn_only=True):
        if run(command0).failed:
            run(command1)
        else:
            # clean old record
            run(command2)
            run(command1)

    pass


def cmd_su(cmd, user=None):
    '''
    bind command for user with `su`
    :param cmd: command
    :param user: username
    '''
    if user:
        return run('su - %s -c "%s"' % (user, cmd))
    else:
        return run(cmd)


def cmd_git(path=None, url=None, branch='master', tag=None, user=None, ignore_perm=True):
    '''
    deploy source code by git
    :param path:
    :param url:
    :param branch:
    :param user:
    :param host_known:
    :param host_bind:
    :param tmpfs: if set tmpfs,this process will write to rc.local @todo auto check
    :return:
    '''

    host_begin = url.find('@')
    host_end = url.find(':')
    request_host = url[host_begin + 1:host_end].strip()

    if url[0:3] == 'git':
        host_known = True
    else:
        host_known = False

    if request_host and host_known:
        cmd_known_host(request_host, user=user)

    parent = os.path.dirname(path)

    with settings(warn_only=True):
        if run("test -d %s" % path).failed:
            with cd(parent):
                cmd_su('git clone {} -b {} {}'.format(url, branch, path), user)
                cmd_su("cd {} && git config core.fileMode false".format(path), user)

    with cd(path):
        with settings(warn_only=True):
            if cmd_su("cd %s && git checkout %s" % (path, branch), user).failed:
                if tag:
                    cmd_su("cd %s && git checkout -- ." % path, user)
                    cmd_su("cd %s && git checkout %s" % (path, branch), user)

        cmd_su("cd %s && git config core.fileMode false" % (path), user)
        cmd_su("cd %s && git pull origin %s" % (path, branch), user)
        cmd_su("cd %s && git pull origin %s --tags" % (path, branch), user)
        if tag:
            cmd_su("cd %s && git checkout %s" % (path, tag), user)

    pass


def cmd_ip(card='eth0'):
    """
    Get network card ip address
    :param eth:
    :return:
    """
    ip = run("ifconfig %s | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'" % card)
    # for debug
    # print "match ip : %s" % ip
    return ip


def yum_install(package_name, newer=None):
    if newer:
        run('yum  --enablerepo={}  install {} -y'.format(newer, package_name))
    else:
        run('yum install {} -y'.format(package_name))
    pass


def wget_install_package(project, version, url, suffix='tar.gz'):
    name = project + '-' + version

    run('wget {1}/{0}.{2} -O /tmp/{0}.{2}'.format(name, url, suffix))

    with cd('/tmp'):
        with settings(warn_only=True):
            if suffix == 'tar.gz':
                run('tar -xvzpf {}.{}'.format(name, suffix))
            elif suffix == 'tar.bz2':
                run('tar -xvjpf {}.{}'.format(name, suffix))


    pass
