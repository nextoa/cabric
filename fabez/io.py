# -*- coding: utf-8 -*-

from fabric.api import *

def io_tmpfs(path,boot=True,size=8,uid='root',gid='root',mode='777'):
    """
    tmpfs function.
    :param path:
    :param boot:
    :param size:
    :param uid:
    :param gid:
    :param mode:
    :return:
    """

    match = "tmpfs    %s" % path
    replace = "%s    tmpfs    uid=root,gid=root,size=%sG,mode=777  0 0" % (match, size)

    if boot is True:
        with settings(warn_only=True):
            run('mkdir %s' % path)
            run('grep "%s" /etc/fstab && sed -i -e "s/%s.*//g" /etc/fstab' % (match, '\/'.join(match.split('/'))))
        run('grep "%s" /etc/fstab || echo "%s" >> /etc/fstab ' % (match, replace))

        with settings(warn_only=True):
            if run('df -h | grep %s' % path).failed:
                run('mount %s' % path)

    pass



def rm_io_tmpfs(path,boot=True):
    with settings(warn_only=True):
        if run('df -h | grep %s' % path):
            run('umount %s' % path)


    if boot is True:
        match = "tmpfs    %s" % path
        with settings(warn_only=True):
            run('grep "%s" /etc/fstab && sed -i -e "s/%s.*//g" /etc/fstab' % (match, '\/'.join(match.split('/'))))
    pass



def io_airlog():
    """
    FastLog
    :return:
    """
    return io_tmpfs('/airlog')



def rm_io_airlog():
    return rm_io_tmpfs('/airlog')



def io_webdata(uid='webuser',gid='webuser'):
    return io_tmpfs('/webdata',uid=uid,gid=gid,mode=700)



def rm_io_webdata():
    return rm_io_tmpfs('/webdata')


