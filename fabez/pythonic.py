# -*- coding: utf-8 -*-



import os
from fabric.api import *
from fabez.utils import (utils_baselib)
from fabez.cmd import (cmd_git)


# @note if name start py, this is install tools

def py_python(tag=None, force=True):
    '''
    install python. include python,setuptools,pip and supervisord
    :param pip_index_url:proxy url
    '''

    utils_baselib()

    run('yum install libtiff-devel libjpeg-devel libzip-devel freetype-devel lcms2-devel libwebp-devel tcl-devel tk-devel -y')

    if tag is None:
        tag_str = '2.7.8'
    else:
        tag_str = tag

    if tag.find('2.7.8') == 0:
        cmd_git('/tmp/python', 'https://github.com/kbonez/python.git', tag=tag)
        cd_path = '/tmp/python'
    else:
        run('wget https://www.python.org/ftp/python/{0}/Python-{0}.tgz -O /tmp/Python-{0}.tgz'.format(tag))
        run('cd /tmp && tar -xvzpf Python-{0}.tgz'.format(tag))
        cd_path = '/tmp/Python-{}'.format(tag)

    with cd(cd_path):
        run('./configure --prefix /usr/local/lib/python/Versions/{}'.format(tag_str))
        run('make && make install')

    if tag_str.find('3') == 0:
        py_pip('/usr/local/lib/python/Versions/{}/bin/python3'.format(tag_str))
        python_fix('/usr/local/lib/python/Versions/{}/bin/python3'.format(tag_str), force=force)
        pip_fix('/usr/local/lib/python/Versions/{}/bin/pip3'.format(tag_str), force=force)
        py_python(tag='2.7.8', force=False)
    else:
        py_pip('/usr/local/lib/python/Versions/{}/bin/python'.format(tag_str))
        python_fix('/usr/local/lib/python/Versions/{}/bin/python'.format(tag_str), force=force)
        pip_fix('/usr/local/lib/python/Versions/{}/bin/pip'.format(tag_str), force=force)
        pip('supervisor', pip_path='/usr/local/lib/python/Versions/{}/bin/pip'.format(tag_str))
        supervisor_fix('/usr/local/lib/python/Versions/{}/bin'.format(tag_str))

    pip('Sphinx')

    if force:
        python_bin_path('/usr/local/lib/python/Versions/{}/bin'.format(tag_str))

    pass


def rm_python():
    """
    @deprecated
        move from pythonic. we don't need it any more.
    :return:
    """

    with settings(warn_only=True):
        pip_uninstall('setuptools')
        run('rm -rf /usr/local/bin/pip*')
        run('rm -rf /usr/local/bin/python*')
        run('rm -rf /usr/local/*/python*')
        run('rm -rf /usr/local/etc/supervisor*')
        run('rm -rf /tmp/python')
        run('rm -rf /tmp/pip')
        run('rm -rf /tmp/setuptools')
    pass


def py_pypy(version='2.4.0'):
    """
    install pypy and pypy tools
    @note  this depends epel resources
    :return:
    """

    # compile form source
    py_python(tag='2.7.8')
    python_fix('/usr/local/lib/python/Versions/2.7.8/bin/python')

    # #### skip install origin python pip
    # ### py_pip('/usr/local/lib/python/Versions/2.7.8/bin/python')

    # @see http://pypy.readthedocs.org/en/latest/build.html#install-build-time-dependencies
    run('yum install gcc make libffi-devel pkgconfig zlib-devel bzip2-devel lib-sqlite3-devel ncurses-devel expat-devel openssl-devel -y')

    run('wget https://bitbucket.org/pypy/pypy/downloads/pypy-{0}-src.tar.bz2 -O /tmp/pypy-{0}-src.tar.bz2'.format(version))
    with cd('/tmp'):
        run('tar -xvjpf pypy-{}-src.tar.bz2'.format(version))
        with cd('/tmp/pypy-{}-src'.format(version)):
            # run('/usr/local/lib/python/Versions/2.7.8/bin/python rpython/bin/rpython -Ojit pypy/goal/targetpypystandalone.py --withoutmod-_minimal_curses')
            run('make && make install')
            pass

    return

    py_pip('/usr/bin/pypy')
    pip_fix('/usr/lib64/pypy-2.0.2/bin/pip')

    pass


def py_setup_py(code_dir=None, python='pypy'):
    '''
    short for cd path && python setup.py install
    :param code_dir: path
    :param python: python path,default is python
    '''
    with cd(code_dir):
        run('%s setup.py build' % python)
        run('%s setup.py install' % python)


def py_pip(python='/usr/bin/pypy'):
    """
    install pip package
    :return:
    """
    run('curl -sS https://gist.githubusercontent.com/9nix00/d70733d0728ce05cf6ed/raw/get-pip.py | %s ' % python)
    pass


# selenium
# 安装chrome driver
# download http://chromedriver.storage.googleapis.com/2.10/chromedriver_mac32.zip
# offical site:  https://sites.google.com/a/chromium.org/chromedriver/downloads




def pip(package=None, upgrade=True, pip_path=None):
    '''
    install package use pip
    :param package: package name
    :param upgrade: true
    '''

    if pip_path is None:
        pip_path = 'pip'

    if package:
        if upgrade:
            run('%s install %s --upgrade' % (pip_path, package))
        else:
            run('%s install %s' % (pip_path, package))


def pip_uninstall(package):
    '''
    uninstall package from pip
    :param package:
    :return:
    '''
    with settings(warn_only=True):
        run('pip uninstall %s -y' % package)


def pip_fix(file_path, force=False):
    if force:
        run('ln -snf {} /usr/local/bin/pip'.format(file_path))
    else:
        run('test -f /usr/local/bin/pip || ln -s {} /usr/local/bin/pip'.format(file_path))

    pass


def python_fix(file_path, force=False):
    if force:
        run('ln -snf {} /usr/local/bin/python'.format(file_path))
    else:
        run('test -f /usr/local/bin/python || ln -s {} /usr/local/bin/python'.format(file_path))

    pass


def supervisor_fix(file_path, force=False):
    if force:
        run('ln -snf {}/supervisord /usr/local/bin/supervisord'.format(file_path))
        run('ln -snf {}/supervisorctl /usr/local/bin/supervisorctl'.format(file_path))
    else:
        run('test -f /usr/local/bin/supervisord || ln -s {}/supervisord /usr/local/bin/supervisord'.format(file_path))
        run('test -f /usr/local/bin/supervisorctl || ln -s {}/supervisorctl /usr/local/bin/supervisorctl'.format(file_path))

    pass


def python_path(path, user=''):
    """
    set private package path
    @note if you use this, you mustn't manual set your PYTHONPATH in your .bash_profile

    :param user:
    :return:
    """
    with settings(warn_only=True):
        run('sed -i -e "s/^export PYTHONPATH.*//g" ~{}/.bash_profile'.format(user))
        if run('cat ~{}/.bash_profile | grep "^export PYTHONPATH"'.format(user)).failed:
            run('echo "export PYTHONPATH=\"{}\"" >> ~{}/.bash_profile'.format(path, user))

        if user:
            run('chown -Rf {}.{} ~{}/.bash_profile'.format(user, user, user))


def python_bin_path(path, user=''):
    """
    set private package path
    @note if you use this, you mustn't manual set your PATH in your .bash_profile

    :param user:
    :return:
    """
    with settings(warn_only=True):
        run('sed -i -e "s/^export PATH=\/usr\/local\/lib\/python.*//g" ~{}/.bash_profile'.format(user))
        if run('cat ~{}/.bash_profile | grep "^export PATH=\/usr\/local\/lib\/python"'.format(user)).failed:
            run('echo "export PATH=\"{}:$PATH\"" >> ~{}/.bash_profile'.format(path, user))

        if user:
            run('chown -Rf {}.{} ~{}/.bash_profile'.format(user, user, user))






