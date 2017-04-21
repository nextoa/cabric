# -*- coding: utf-8 -*-

import json
import os

from cliez.component import Component
from fabric.context_managers import settings, cd

from cabric.utils import get_roots, mirror_put, run, \
    bind_hosts, execute, get_platform, run_block, \
    exist_group, exist_user

try:
    from shlex import quote as shell_quote
except ImportError:
    from pipes import quote as shell_quote


class InstallComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    system_python_version = '2.7.11'

    def before_install(self, root):
        mirror_put(root, '/etc/hosts', validate=False)
        mirror_put(root, '/root/.bash_profile', validate=False)
        pass

    def install_user(self, users):
        """
        install user

        ..note::

            user will only install on linux machine.

        :return:
        """

        def on_centos():
            """
            workflow

            * parse config and set default value
                * force set shell to /sbin/nologin when system flag is set
                * cause error when config.name not exists
            * skip create when user exists
            * create group explicitly
                when user specify and not same config.name

            :return:
            """
            for user in users:
                username = user.get('name')
                groupname = user.get('group', username)
                home = user.get('home', '/home/{}'.format(username))
                shell = user.get('shell', '`which bash`')
                system_flag = user.get('system', False)
                perm = user.get('perm')

                if system_flag:
                    shell = '/sbin/nologin'

                if not username:
                    self.error("invalid user config")

                if exist_user(username):
                    if perm:
                        run('chmod {1} {0}'.format(home, perm))
                    self.warn("user `%s' exist.skip to create." % username)
                    continue

                system_str = '-r' if system_flag else ''

                if groupname == username:
                    group_str = '-U'
                else:
                    if not exist_group(groupname):
                        run('groupadd {1} {0}'.format(groupname, system_str))
                        pass
                    group_str = '-g {}'.format(groupname)

                run('useradd {1} -d {2} {4} -s {3} {0}'.format(username,
                                                               group_str,
                                                               home, shell,
                                                               system_str))

                # todo:
                # .. if perm cause error, user will not delete
                if perm:
                    run('chmod {1} {0}'.format(home, perm))

                pass

        run_block(centos=on_centos)
        pass

    def install_package(self, root, pkgs_config):
        """
        install system package
        workflow:
            - try add gpg key
            - yum install
            - yum localinstall

        :param root: pkgs_config root directory path
        :param pkgs_config: package.json pkgs_config
        :return:
        """

        def on_centos():
            rpm_keys = pkgs_config.get('rpm-keys', [])
            if rpm_keys:
                for v in rpm_keys:
                    run("rpm --import %s" % v)
                    pass
                pass

            pkg = pkgs_config.get('yum')
            if pkg:
                mirror_put(root, '/etc/yum.repos.d', validate=False)
                run('yum install -y epel-release')
                run('yum install -y %s' % ' '.join(pkg))

            pkg_local = pkgs_config.get('yum-local', [])
            for p in pkg_local:
                with cd("/tmp"):
                    run("curl -L -O %s" % p)
                    run('yum localinstall -y %s' % os.path.basename(p))
                    pass
                pass
            pass

        def on_mac():
            pkg = pkgs_config.get('brew')
            if not pkg:
                return

            with settings(warn_only=True):
                run('brew install %s' % ' '.join(pkg))

            pass

        run_block(centos=on_centos, mac=on_mac)
        pass

    def install_pyenv(self, versions=None, skip_pkg=False):
        """
        We will install pyenv by default. and with normal use lib

        Because pyenv is awesome!!!

        :param root:
        :param skip_pkg: skip install depends package, default is False

        :return:
        """
        remote_os = get_platform()

        if remote_os == 'centos':
            if not skip_pkg:
                run('yum install -y git')
                run("yum install -y gcc gcc-c++ make autoconf certbot"
                    " libffi-devel ncurses-devel expat-devel"
                    " zlib-devel zlib libzip-devel"
                    " bzip2 bzip2-devel bzip2-libs"
                    " mariadb-devel mariadb-libs"
                    " sqlite-devel lib-sqlite3-devel"
                    " libxml2 libxml2-devel libxslt libxslt-devel"
                    " libcurl-devel"
                    " pcre_devel pcre"
                    " libmcrypt libmcrypt-devel openssl-devel openssl-lib"
                    " libjpeg libjpeg-devel libpng libpng-devel"
                    " freetype freetype-devel "
                    " libtiff-devel lcms2-devel libwebp-devel"
                    " tcl-devel tk-devel"
                    )
            run('export PYENV_ROOT=/usr/local/var/pyenv && '
                'curl -L https://raw.githubusercontent.com'
                '/yyuu/pyenv-installer/master/bin/pyenv-installer | bash')
            run('ln -sfv /usr/local/var/pyenv/bin/pyenv /usr/local/bin/pyenv')

            pass
        elif remote_os == 'mac':
            with settings(warn_only=True):
                run('brew install git pyenv')
            pass

        run('test -d /usr/local/var/pyenv/plugins/pyenv-virtualenv ||'
            ' git clone https://github.com/yyuu/pyenv-virtualenv.git'
            ' /usr/local/var/pyenv/plugins/pyenv-virtualenv')

        run('export PYENV_ROOT="/usr/local/var/pyenv/" &&'
            ' eval "$(pyenv init -)"')

        if isinstance(versions, list):
            for v in versions:
                run('export PYENV_ROOT="/usr/local/var/pyenv/" &&'
                    ' pyenv install -s %s' % v)
        elif type(versions).__name__ in ['str', 'unicode']:
            run('export PYENV_ROOT="/usr/local/var/pyenv/" &&'
                ' pyenv install -s %s' % versions)
        else:
            run('export PYENV_ROOT="/usr/local/var/pyenv/" && '
                'pyenv install -s %s' % self.system_python_version)

        command_list = [
            """grep "PYENV_ROOT" /etc/profile || \
            echo 'export PYENV_ROOT="/usr/local/var/pyenv/"' \
            >> /etc/profile""",
            """grep "pyenv init" /etc/profile || \
            echo 'eval "$(pyenv init -)"' >> \
            /etc/profile""",
            """grep "pyenv virtualenv" /etc/profile || \
            echo 'eval "$(pyenv virtualenv-init -)"' \
            >> /etc/profile""",
        ]

        if remote_os == 'mac':
            command_list = ["sudo sh -c '%s'" % shell_quote(v) for v in
                            command_list]
            pass

        for cmd in command_list:
            run(cmd)
            pass

        pass

    def install_pypi(self, pypi_configs, skip_pkg=False):
        """
        :param pip_configs:
        :param skip_pkg: skip install depends package, default is False
        :return:
        """

        def install(pypi_config):

            python_version = pypi_config.get('version')

            if python_version:
                self.install_pyenv(python_version, skip_pkg)

            used_version = python_version \
                if python_version else self.system_python_version

            for pkg in pypi_config.get('packages'):
                run('export PYENV_ROOT="/usr/local/var/pyenv/" && '
                    'export PYENV_VERSION=%s && '
                    'pip install %s' % (used_version, pkg))
                pass

            pass

        [install(pypi_config) for pypi_config in pypi_configs]
        pass

    def install_node(self, root, pkgs_config, skip_pkg=False):
        """
        global node package denends

        ..note::

            this will install global package.

        :param root: pkgs_config root directory path
        :param pkgs_config: package.json pkgs_config
        :param skip_pkg: skip install depends package, default is False
        :return:
        """

        pkg = pkgs_config.get('node')
        if not pkg:
            return

        def on_centos():
            if not skip_pkg:
                run('yum install -y epel-release')
                run('yum install -y nodejs npm')
            pass

        def on_mac():
            if skip_pkg:
                run('brew install node')
            pass

        def on_all():
            """
            plan feature
            support add extra repo source
            :return:
            """
            # npm_bin = run('which npm')
            # npm_root = npm_bin.rsplit('/', 2)[0]
            # npm_etc = os.path.join(npm_root, 'etc')
            # print(npm_root)
            run('npm install -g %s' % ' '.join(pkg))
            pass

        run_block(centos=on_centos, mac=on_mac, all=on_all)
        pass

    def run(self, options):
        """
        workflow

            * try upload repo config if it can recognize
            * execute install
            * create user if not exists (only on linux machine)
            * execute custom script
            * enable register service
            * finish

        :param options:
        :return:
        """

        package_root, config_root, fabric_root = get_roots(options.dir)
        bind_hosts(fabric_root, options.env, options.parallel)

        # try upload repo config if it can recognize
        using_config = os.path.join(config_root, options.env)

        try:
            packages_config = json.load(
                open(os.path.join(package_root, options.env, 'packages.json'),
                     'r'))
        except ValueError:
            self.error("Invalid json"
                       " syntax:%s" % os.path.join(package_root,
                                                   options.env,
                                                   'packages.json'))

        try:
            env_config = json.load(
                open(os.path.join(package_root, options.env, 'env.json'), 'r'))
        except ValueError:
            self.error("Invalid json"
                       " syntax:%s" % os.path.join(package_root,
                                                   options.env,
                                                   'env.json'))

        execute_list = []

        execute_list.append(lambda: self.before_install(using_config))

        if not options.skip_pkg:
            execute_list.append(
                lambda: self.install_package(using_config, packages_config))

        if not options.skip_pyenv:
            execute_list.append(
                lambda: self.install_pyenv(packages_config.get('pyenv'),
                                           options.skip_pkg))

        if not options.skip_pypi:
            execute_list.append(
                lambda: self.install_pypi(packages_config.get('pypi', []),
                                          options.skip_pkg))

        if not options.skip_node:
            execute_list.append(
                lambda: self.install_node(using_config, packages_config,
                                          options.skip_pkg))

        if not options.skip_user:
            execute_list.append(
                lambda: self.install_user(env_config.get('users', [])))

        if execute_list:
            execute(execute_list)
        else:
            self.print_message("nothing to do.")

        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('--skip-pkg',),
             dict(action='store_true', help='skip install pkg', )),
            (('--skip-pyenv',),
             dict(action='store_true', help='skip install pyenv', )),
            (('--skip-node',),
             dict(action='store_true', help='skip install node', )),
            (('--skip-user',),
             dict(action='store_true', help='skip install user', )),
            (('--skip-pypi',),
             dict(action='store_true', help='skip install pip package', )),
            (('--parallel', '-P'), dict(action='store_true',
                                        help='default to parallel execution'
                                             ' method', )),
        ]
        pass

    pass
