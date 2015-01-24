# -*- coding: utf-8 -*-

from fabric.api import *
from cabric.cmd import cmd_expanduser,cmd_su
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

    if user:
        user_path = cmd_expanduser(user)
    else:
        user_path = '~'

    remote_root = '%s/.ssh' % user_path
    remote_path = '%s/authorized_keys' % remote_root

    with settings(warn_only=True):
        if run('test -d %s' % remote_root).failed:
            cmd_su('mkdir %s' % remote_root, user)
            if user:
                run('chown %s.%s %s' % (user, user, remote_root))

    put(path, '/tmp/tmp.pub', mode=0644)
    cmd_su('grep %s %s | cat /tmp/tmp.pub >> %s' % (mail, remote_path, remote_path),user)
    if user:
        run('chown %s.%s %s' % (user, user, remote_path))

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
        # valid key type
        fp = open(os.path.expanduser(path))
        private_key = fp.read()
        pos = private_key.find("\n")

        if private_key[0:pos].find('DSA') > -1:
            dsa = True
        else:
            dsa = False

    user_path = cmd_expanduser(user)

    remote_root = '%s/.ssh' % user_path

    if dsa:
        remote_path = '%s/id_dsa' % remote_root
    else:
        remote_path = '%s/id_rsa' % remote_root

    with settings(warn_only=True):
        if run('test -d %s' % remote_root).failed:
            if user:
                run('chown -Rf %s.%s %s' % (user, user, user_path))
            cmd_su('mkdir %s' % remote_root,user)

    put(path, remote_path, mode=0600)
    if user:
        run('chown %s.%s %s' % (user, user, remote_path))
    pass

