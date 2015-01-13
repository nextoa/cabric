# -*- coding: utf-8 -*-

from fabric.api import *
import os



def classic_userexist(user):
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


def classic_useradd(user,shell='`which bash`',extra=[],**kwargs):
    """
    Remote UserAdd
    :param user: username
    :param extra: extra
    :return:
    """

    if classic_userexist(user) is False:
        run('useradd %s -d /home/%s -s %s ' % (user,user,shell))
        run('mkdir /home/%s && chown %s.%s /home/%s' % (user,user,user,user))

        with settings(warn_only=True):
            for dir in extra:
                if run("test -d %s" % dir).failed:
                    run('mkdir %s' % dir)
                run('chown -Rf %s.%s %s' % (user,user,dir))


    pass



def classic_userdel(user,clean=True,extra=[]):
    """
    clean user files
    :param user:
    :param clean:
    :param extra:
    :return:
    """

    if classic_userexist(user) is False:
        raise "User %s not exits" % user

    if clean is True:
        run('userdel -r %s' % user)
    else:
        run('userdel  %s' % user)

    with settings(warn_only=True):
        for dir in extra:
            run("rm -rf  %s" % dir)

    pass




def classic_git(proxy=None):
    '''
    Install git
    :param proxy:proxy server
    :return:
    '''
    run('yum install git -y')

    if proxy:
        run('git config --global http.proxy {}'.format(proxy))

    pass


def rm_classic_git():
    '''
    remove git and git config
    :return:
    '''
    with settings(warn_only=True):
        run('yum erase git -y')
        run('rm -rf ~/.gitconfig')



def classic_baselib():
    '''
    install base package
    :return:
    '''
    run(
        'yum install gcc-c++ make zlib-devel libxml2  libxml2-devel  bzip2-libs bzip2-devel  libcurl-devel  libjpeg libjpeg-devel  libpng libpng-devel  freetype freetype-devel  libmcrypt libmcrypt-devel  libtool-ltdl libtool-ltdl-devel openssl-devel -y')
    run('mkdir -p /usr/local/var/run')
    run('grep "ulimit" /etc/rc.local || echo "ulimit -SHn 65535" >> /etc/rc.local')

    pass



def classic_ulimit(limit=65535):
    """
    add ulimit for heavy load system
    :return:
    """
    with settings(warn_only=True):
        if run('cat /etc/security/limits.d/90-nproc.conf | grep %s' % "'*          soft    nproc'").failed:
            run("echo '%s%d >> /etc/security/limits.d/90-nproc.conf'" % ("'*          soft    nproc     '",limit))
        else:
            run('sed -i -e "s/*          soft    nproc     \d+/*          soft    nproc     %d/g" /etc/security/limits.d/90-nproc.conf' % limit)




    pass





def classic_expanduser(user=None):
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




def classic_bind_host(ip=None,name=None):
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


def rm_classic_bind_host(ip=None,name=None):
    '''
    clean user bind ip-host
    :return:
    '''
    with settings(warn_only=True):
        match = '%s %s' % (ip,name)
        if run('grep "%s" /etc/hosts' % match):
            run('sed -i -e "s/%s//g" /etc/hosts' % match)

    pass



def classic_known_host(name,user=None):
    '''
    set ssh figerprint
    :param name:domain
    :param user:webuser
    '''

    user_path = classic_expanduser(user)
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


def classic_user_cmd(cmd,user=None):
    '''
    bind command for user with `su`
    :param cmd: command
    :param user: username
    '''
    if user:
        return 'su - %s -c "%s"' % (user,cmd)
    else:
        return cmd



def classic_gito(path=None, url=None, branch='master',user=None,host_bind=None,tmpfs=None):
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

    if host_bind:
        # @todo 后期加入http协议的逻辑
        bind_host(host_bind,request_host)
        pass


    if url[0:3] == 'git':
        host_known=True
    else:
        host_known=False


    if request_host and host_known:
        known_host(request_host,user=user)


    parent = os.path.dirname(path)

    git_clone=user_cmd('git clone {} -b {} {}'.format(url, branch,path),user)

    with settings(warn_only=True):
        if run("test -d %s" % path).failed:
            with cd(parent):
                run(git_clone)

    # with cd(path):
    run(user_cmd("cd %s && git pull" % path,user))

    #基于内存盘的，需要添加rc.local，有点不完美的地方，这个应该添加在supvisor之前
    if tmpfs:
        run("grep '%s' /etc/rc.local || echo '%s' >> /etc/rc.local" % (git_clone,git_clone))
        pass



def put_private_key(path=None, user=None):
    """
    Upload private key to remote server
    Limit: Must be a standard key generate from ssh-keygen
    :param path:local path
    :param user:remote username
    """
    if os.path.exists(os.path.expanduser(path)) is False:
        abort("private key not exist")
    else:
        # 通过解读key来判断是rsa还是dsa格式
        fp = open(os.path.expanduser(path))
        private_key = fp.read()
        pos = private_key.find("\n")

        if private_key[0:pos].find('DSA') > -1:
            dsa = True
        else:
            dsa = False

    user_path=expanduser(user)

    remote_root = '%s/.ssh' % user_path


    if dsa:
        remote_path = '%s/id_dsa' % remote_root
    else:
        remote_path = '%s/id_rsa' % remote_root

    with settings(warn_only=True):
        if run('test -d %s' % remote_root).failed:
            run('chown -Rf %s.%s %s' % (user,user, user_path))
            run('su - %s -c "mkdir %s"' % (user, remote_root))


    put(path, remote_path, mode=0600)
    run('chown %s.%s %s' % (user,user,remote_path))
    pass


def put_public_key(path=None, user=None):
    """
    Upload pub key from remote server.
    Limit: Openssh standard key,must comment with user mail.
    :param path:local path
    :param user:remote username
    :return:
    """
    if os.path.exists(os.path.expanduser(path)) is False:
        abort("public key not exist")
    else:
        # 通过解读最后注释来判断key是否存在，如果不存在注释，判断为非法的key
        fp = open(os.path.expanduser(path))
        pub_key = fp.read()
        pos = pub_key.rfind(" ")

        mail = pub_key[pos + 1:].strip()
        if mail.find('@') == -1:
            abort('please add comment WHO YOU ARE.')


    user_path=expanduser(user)

    remote_root = '%s/.ssh' % user_path
    remote_path = '%s/authorized_keys' % remote_root

    with settings(warn_only=True):
        if run('test -d %s' % remote_root).failed:
            run('su - %s -c "mkdir %s"' % (user, remote_root))
            run('chown %s.%s %s' % (user,user, remote_root))


    put(path, '/tmp/tmp.pub', mode=0644)
    run('su - %s -c "grep %s %s | cat /tmp/tmp.pub >> %s"' % (user, mail,remote_path, remote_path))
    run('chown %s.%s %s' % (user,user,remote_path))


    pass

