# -*- coding: utf-8 -*-

from fabric.api import *


def io_tmpfs(path, boot=True, size=8, uid='root', gid='root', mode='777'):
    """
    tmpfs function.
    @todo uid,gid feature
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
            run('mkdir -p %s' % path)
            run('grep "%s" /etc/fstab && sed -i -e "s/%s.*//g" /etc/fstab' % (match, '\/'.join(match.split('/'))))
        run('grep "%s" /etc/fstab || echo "%s" >> /etc/fstab ' % (match, replace))

        with settings(warn_only=True):
            if run('df -h | grep %s' % path).failed:
                run('mount %s' % path)

    pass


def rm_io_tmpfs(path, boot=True):
    with settings(warn_only=True):
        if run('df -h | grep %s' % path):
            run('umount %s' % path)

    if boot is True:
        match = "tmpfs    %s" % path
        with settings(warn_only=True):
            run('grep "%s" /etc/fstab && sed -i -e "s/%s.*//g" /etc/fstab' % (match, '\/'.join(match.split('/'))))
    pass


def io_disk(real_path, uid=None, gid=None, mode='777'):
    """
    base function
    :param real_path:
    :param uid:
    :param gid:
    :param mode:
    :return:
    """
    with settings(warn_only=True):
        run('mkdir -p {}'.format(real_path))

    if gid is None:
        gid = uid

    if uid is None:
        run('chmod {} -Rf {}'.format(mode, real_path))
    else:
        run('chown -Rf {}.{} {} '.format(uid, gid, real_path))
        run('chmod 700 -Rf {}'.format(real_path))

    pass


def rm_io_disk(path):
    return run('rm -rf %s' % path)


def io_airlog():
    """
    FastLog
    :return:
    """
    return io_tmpfs('/airlog')


def rm_io_airlog():
    return rm_io_tmpfs('/airlog')


def io_webdata(uid='webuser', gid='webuser', tmpfs=False):
    if tmpfs:
        return io_tmpfs('/webdata', uid=uid, gid=gid, mode=700)
    else:
        return io_disk('/webdata', uid=uid, gid=gid)


def rm_io_webdata(uid='webuser', gid='webuser', tmpfs=False):
    if tmpfs:
        return rm_io_tmpfs('/webdata', uid=uid, gid=gid)
    else:
        return rm_io_disk('/webdata', uid=uid, gid=gid)


def io_slowlog(path, user=None):
    """
    create slow log system
    :return:
    """

    real_path = '/logs/%s' % path
    return io_disk(real_path, uid=user)
    pass


def rm_io_slowlog(path):
    return rm_io_disk(path)


def io_aircache(path, size=1):
    """
    create air cache
    :return:
    """

    real_path = '/aircache/%s' % path
    return io_tmpfs(real_path, size=size)


def io_aircache(path, size=1):
    """
    create air cache
    :return:
    """

    real_path = '/aircache/%s' % path
    return io_tmpfs(real_path, size=size)


def rm_io_aircache(path):
    return rm_io_tmpfs(path)


def io_socks(path, user=None):
    """
    create slow log system
    :return:
    """

    real_path = '/usr/local/var/run/%s' % path
    io_disk(real_path, uid=user)
    pass


def rm_io_socks(path):
    return rm_io_disk(path)


def _valid_partition(partition):
    try:
        int(partition[-1])
    except:
        print("partition should be real partition,not device.")
        raise
    pass


def io_big_disk(device, label='gpt', rebuild=False):
    """
    force limit 1 partition
    :param device:
    :param label:
    :param rebuild:
    :return:
    """
    if not rebuild:
        run('parted {} "mklabel {}"'.format(device, label))

    if rebuild:
        run('parted {} rm 1'.format(device))

    run('parted {} "mkpart primary 1049K -1"'.format(device))

    if rebuild:

        run('e2fsck -f {}1 && resize2fs {}1'.format(device))

    pass


def io_format_disk(partition, fs_type='xfs',force=True):
    """
    :param device:
    :param fs_type:
    :return:
    """

    _valid_partition(partition)

    if force:
        run('mkfs.{} -f {}'.format(fs_type, partition))
    else:
        run('mkfs.{} {}'.format(fs_type, partition))


    pass


def io_mount_disk(partition, mount_path, partition_format='xfs'):
    """

    @todo uid,gid feature
    :param path:
    :param boot:
    :param size:
    :param uid:
    :param gid:
    :param mode:
    :return:
    """

    _valid_partition(partition)

    match = "UUID=`blkid {} | awk -F '\"' '{{print $2}}'` {}".format(partition, mount_path)

    replace = "{}  {}  defaults  0 2".format(match, partition_format)

    with settings(warn_only=True):
        run('mkdir -p %s' % mount_path)
        run('grep "%s" /etc/fstab && sed -i -e "s/%s.*//g" /etc/fstab' % (match, '\/'.join(match.split('/'))))
    run('grep "%s" /etc/fstab || echo "%s" >> /etc/fstab ' % (match, replace))

    with settings(warn_only=True):
        if run('df -h | grep %s' % mount_path).failed:
            run('mount %s' % mount_path)

    pass


def io_umount_disk(path):

    with settings(warn_only=True):
        if run('df -h | grep %s' % path):
            run('umount %s' % path)

    with settings(warn_only=True):
        run('grep "%s" /etc/fstab && sed -i -e "s/.*%s.*//g" /etc/fstab' % (path, '\/'.join(path.split('/'))))
    pass



# for mini machine
# https://www.digitalocean.com/community/tutorials/how-to-add-swap-on-centos-6
# 5个G
# dd if=/dev/zero of=/swapfile bs=10240 count=512k
# mkswap /swapfile
# /etc/fstab
# /swapfile          swap            swap    defaults        0 0

# chown root:root /swapfile
# chmod 0600 /swapfile


