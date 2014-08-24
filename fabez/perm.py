# -*- coding: utf-8 -*-

from fabric.api import *
from fabez.cmd import cmd_expanduser
import os


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


    user_path=cmd_expanduser(user)

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

    user_path=cmd_expanduser(user)

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

