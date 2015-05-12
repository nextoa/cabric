# -*- coding: utf-8 -*-



import os
from fabric.api import *
from cabric.utils import (utils_baselib)
from cabric.cmd import (cmd_git, yum_install)


# @note if name start py, this is used to install tools

def py_python(tag='3.4.2', force=True, compatible=True, pypy='2.4'):
    """
    install python. include python,setuptools,pip and supervisord
    :param pip_index_url:proxy url
    """

    utils_baselib()

    run('wget https://www.python.org/ftp/python/{0}/Python-{0}.tgz -O /tmp/Python-{0}.tgz'.format(tag))
    run('cd /tmp && tar -xvzpf Python-{0}.tgz'.format(tag))
    cd_path = '/tmp/Python-{}'.format(tag)

    with cd(cd_path):
        run('./configure --prefix /usr/local/lib/python/Versions/{}'.format(tag))
        run('make && make install')

    if tag.find('3') == 0:
        # python3 already included pip
        # py_pip('/usr/local/lib/python/Versions/{}/bin/python3'.format(tag))
        python_fix('/usr/local/lib/python/Versions/{}/bin/python3'.format(tag), force=force)

        if compatible:
            pip_fix('/usr/local/lib/python/Versions/{}/bin/pip3'.format(tag), force=force, replace='pip3')
            # use pypy instead python2
            if pypy:
                py_pypy(pypy)
        else:
            pip_fix('/usr/local/lib/python/Versions/{}/bin/pip3'.format(tag), force=force)
            pip('Sphinx', pip_path='/usr/local/lib/python/Versions/{}/bin/pip3'.format(tag))

    else:
        py_pip('/usr/local/lib/python/Versions/{}/bin/python'.format(tag))
        python_fix('/usr/local/lib/python/Versions/{}/bin/python'.format(tag), force=force)
        pip_fix('/usr/local/lib/python/Versions/{}/bin/pip'.format(tag), force=force)
        # pip('supervisor', pip_path='/usr/local/lib/python/Versions/{}/bin/pip'.format(tag))
        # supervisor_fix('/usr/local/lib/python/Versions/{}/bin'.format(tag))
        pip('Sphinx', pip_path='/usr/local/lib/python/Versions/{}/bin/pip'.format(tag))

    if force:
        python_bin_path('/usr/local/lib/python/Versions/{}/bin'.format(tag))

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
        # run('rm -rf /usr/local/etc/supervisor*')
        run('rm -rf /tmp/python')
        run('rm -rf /tmp/pip')
        run('rm -rf /tmp/setuptools')
    pass


def py_pypy(version='2.4', server='https://github.com/nextoa/portable-pypy-arch/blob/master'):
    run('wget {1}/pypy-{0}-linux_x86_64-portable.tar.bz2?raw=true -O /tmp/pypy-{0}-linux_x86_64-portable.tar.bz2'.format(version, server))

    run('cd /tmp && tar -xvjpf pypy-{}-linux_x86_64-portable.tar.bz2'.format(version))
    run('rsync -r /tmp/pypy-{0}-linux_x86_64-portable/ /usr/local/pypy-{0}-linux_x86_64-portable'.format(version))

    py_pip('/usr/local/pypy-{0}-linux_x86_64-portable/bin/pypy'.format(version))
    python_fix('/usr/local/lib/python/Versions/{}/bin/pypy'.format(version), force=True, replace='pypy')
    pip_fix('/usr/local/pypy-{0}-linux_x86_64-portable/bin/pip'.format(version), force=True)
    # pip('supervisor', pip_path='/usr/local/pypy-{0}-linux_x86_64-portable/bin/pip'.format(version))
    # supervisor_fix('/usr/local/pypy-{0}-linux_x86_64-portable/bin'.format(version), force=True)

    run('ln -snf /usr/local/pypy-{0}-linux_x86_64-portable /usr/local/pypy'.format(version))

    pip('Sphinx')

    pass


def py_pypy_deprecated(version='2.4.0'):
    """
    install pypy and pypy tools
    only use to refer
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


def py_pip(python='/usr/local/bin/pypy'):
    """
    install pip package
    :return:
    """
    run('curl -sS https://raw.githubusercontent.com/nextoa/get-pip/master/get-pip.py | %s ' % python)
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

        if package.lower() in ['pillow', 'uwsgi']:
            return pip_c(package, upgrade=upgrade, pip_path=pip_path)

        if package.lower() in ['mysqlclient']:
            return pip_hack_mysql(package, upgrade=upgrade, pip_path=pip_path)

        if package.lower() in ['lxml']:
            yum_install('libxslt-devel libxml2-devel')

        if upgrade:
            run('%s install %s --upgrade' % (pip_path, package))
        else:
            run('%s install %s' % (pip_path, package))


def pip3(package=None, upgrade=True):
    """
    short alias for  pip(...,pip_path='pip3')
    :param package:
    :param upgrade:
    :return:
    """

    return pip(package=package, upgrade=upgrade, pip_path='pip3')


def pip_c(pkg_name, upgrade=True, pip_path='pip'):
    """
    some package need c include
    :param pkg_name:
    :return:
    """

    pip_path = run('readlink -f `which {}`'.format(pip_path))
    python_dir = pip_path.rsplit('/', 2)[0]

    if upgrade:
        run('export C_INCLUDE_PATH={0}/include && export CPLUS_INCLUDE_PATH={0}/include && {1} install {2} -U && echo "C_INCLUDE_PATH is:" $C_INCLUDE_PATH'.format(python_dir, pip_path, pkg_name))
    else:
        run('export C_INCLUDE_PATH={0}/include && export CPLUS_INCLUDE_PATH={0}/include && {1} install {2} && echo "C_INCLUDE_PATH is:" $C_INCLUDE_PATH'.format(python_dir, pip_path, pkg_name))

    pass


def pip_hack_mysql(pkg_name, upgrade=True, pip_path='pip'):


    run('yum install mysql-devel -y')

    pip_path = run('readlink -f `which {}`'.format(pip_path))
    python_dir = pip_path.rsplit('/', 2)[0]

    command = 'export DYLD_LIBRARY_PATH="/usr/lib64/mysql" && {0} install {1}'.format(pip_path, pkg_name)

    if upgrade:
        command += ' -U'
        pass

    run(command)
    pass


def pip_uninstall(package):
    '''
    uninstall package from pip
    :param package:
    :return:
    '''
    with settings(warn_only=True):
        run('pip uninstall %s -y' % package)


def pip_fix(file_path, force=False, replace='pip'):
    if force:
        run('ln -snf {} /usr/local/bin/{}'.format(file_path, replace))
    else:
        run('test -f /usr/local/bin/{1} || ln -s {0} /usr/local/bin/{1}'.format(file_path, replace))

    pass


def pip_requirements(file='requirements.txt', upgrade=True, pip_path=None):
    f = os.path.realpath(os.path.expanduser(file))

    with open(f, 'r') as fp:
        buffer = fp.read()

    packages_list = buffer.strip("\n").split("\n")
    depends = []

    for p in packages_list:
        if p and p.find('#') == -1:
            depends.append(p)

    for p in depends:
        pip(p, upgrade, pip_path)

    pass


def pip3_requirements(file='requirements.txt', upgrade=True):
    """
    short alias for pip_requirements(...,pip_path='pip3')
    :param file:
    :param upgrade:
    :return:
    """

    return pip_requirements(file=file, upgrade=upgrade, pip_path='pip3')


def python_fix(file_path, force=False, replace='python'):
    if force:
        run('ln -snf {} /usr/local/bin/{}'.format(file_path, replace))
    else:
        run('test -f /usr/local/bin/{1} || ln -s {0} /usr/local/bin/{1}'.format(file_path, replace))

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






