# -*- coding: utf-8 -*-

from fabric.api import *
import os



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


def cmd_useradd(user,shell='`which bash`',extra=[],**kwargs):
    """
    Remote UserAdd
    :param user: username
    :param extra: extra
    :return:
    """

    if cmd_userexist(user) is False:
        run('useradd %s -d /home/%s -s %s ' % (user,user,shell))
        run('mkdir /home/%s && chown %s.%s /home/%s' % (user,user,user,user))

        with settings(warn_only=True):
            for dir in extra:
                if run("test -d %s" % dir).failed:
                    run('mkdir %s' % dir)
                run('chown -Rf %s.%s %s' % (user,user,dir))


    pass



def cmd_userdel(user,clean=True,extra=[]):
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
    add ulimit for heavy load system.
    use * instead user
    :return:
    """
    with settings(warn_only=True):
        if run('cat /etc/security/limits.d/90-nproc.conf | grep %s' % "'*          soft    nproc'").failed:
            print '%s%d >> /etc/security/limits.d/90-nproc.conf' % ("'*          soft    nproc     '",limit)
        else:
            run('sed -i -e "s/*          soft    nproc     \d+/*          soft    nproc     %d/g" /etc/security/limits.d/90-nproc.conf' % limit)

        if run('cat /etc/security/limits.d/90-nproc.conf | grep %s' % "'*          soft    nofile'").failed:
            print '%s%d >> /etc/security/limits.d/90-nproc.conf' % ("'*          soft    nofile     '",limit)
        else:
            run('sed -i -e "s/*          soft    nproc     \d+/*          soft    nofile     %d/g" /etc/security/limits.d/90-nproc.conf' % limit)



    pass





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




def cmd_bind_host(ip=None,name=None):
    '''
    bind ip-name to /etc/hosts
    :param ip:ip address
    :param name: domain name
    '''
    with settings(warn_only=True):
        match = '%s %s' % (ip,name)
        if run('grep "%s" /etc/hosts' % match).failed:
            run('echo "%s" >> /etc/hosts' % match)

    pass


def rm_cmd_bind_host(ip=None,name=None):
    '''
    clean user bind ip-host
    :return:
    '''
    with settings(warn_only=True):
        match = '%s %s' % (ip,name)
        if run('grep "%s" /etc/hosts' % match):
            run('sed -i -e "s/%s//g" /etc/hosts' % match)

    pass



def cmd_known_host(name,user=None):
    '''
    set ssh figerprint
    :param name:domain
    :param user:webuser
    '''

    user_path = cmd_expanduser(user)
    command0 = 'grep %s %s/.ssh/known_hosts' % (name,user_path)
    command1 = 'ssh-keyscan %s >> %s/.ssh/known_hosts' % (name,user_path)
    command2 = 'sed -i -e "s/%s//g" %s/.ssh/known_hosts' % (name,user_path)


    if user:
        command0 = 'su - %s -c "%s"' % (user,command0)
        command1 = 'su - %s -c "%s"' % (user,command1)
        command2 = 'su - %s -c "%s"' % (user,command2)
        pass


    with settings(warn_only=True):
        if run(command0).failed:
            run(command1)
        else:
            # clean old record
            run(command2)
            run(command1)

    pass


def cmd_su(cmd,user=None):
    '''
    bind command for user with `su`
    :param cmd: command
    :param user: username
    '''
    if user:
        return 'su - %s -c "%s"' % (user,cmd)
    else:
        return cmd



def cmd_git(path=None, url=None, branch='master',user=None):
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
    request_host=url[host_begin+1:host_end].strip()

    if url[0:3] == 'git':
        host_known=True
    else:
        host_known=False

    if request_host and host_known:
        cmd_known_host(request_host,user=user)


    parent = os.path.dirname(path)

    git_clone=cmd_su('git clone {} -b {} {}'.format(url, branch,path),user)

    with settings(warn_only=True):
        if run("test -d %s" % path).failed:
            with cd(parent):
                run(git_clone)

    # with cd(path):
    run(cmd_su("cd %s && git pull" % path,user))



def cmd_ip(card='eth0'):
    """
    Get network card ip address
    :param eth:
    :return:
    """
    ip=run("ifconfig %s | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'" % card)
    # for debug
    # print "match ip : %s" % ip
    return ip




