# -*- coding: utf-8 -*-

import os
import sys

import json
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform, run_block
from fabric.context_managers import settings

try:
    from shlex import quote as shell_quote
except ImportError:
    from pipes import quote as shell_quote


class InstallComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    system_python_version = '2.7.11'

    def install_package(self, root, pkgs_config):
        """
        install system package

        :param root: pkgs_config root directory path
        :param pkgs_config: package.json pkgs_config
        :return:
        """

        def on_centos():
            pkg = pkgs_config.get('yum')
            if not pkg:
                return

            mirror_put(root, '/etc/yum.repos.d', validate=False)
            run('yum install -y %s' % ' '.join(pkg))
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

    def install_pyenv(self):
        """
        We will install pyenv by default. and repla

        Because pyenv is awesome!!!

        :param root:
        :return:
        """
        remote_os = get_platform()

        if remote_os == 'centos':
            run('yum install -y git')
            run('export PYENV_ROOT=/usr/local/var/pyenv && curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash')
            run('ln -sfv /usr/local/var/pyenv/bin/pyenv /usr/local/bin/pyenv')
            pass
        elif remote_os == 'mac':
            with settings(warn_only=True):
                run('brew install git pyenv')
            pass

        run('test -d /usr/local/var/pyenv/plugins/pyenv-virtualenv || git clone https://github.com/yyuu/pyenv-virtualenv.git /usr/local/var/pyenv/plugins/pyenv-virtualenv')
        run('export PYENV_ROOT="/usr/local/var/pyenv/" && eval "$(pyenv init -)"')
        run('export PYENV_ROOT="/usr/local/var/pyenv/" && pyenv install %s' % self.system_python_version)

        command_list = [
            """grep "PYENV_ROOT" /etc/profile || echo 'export PYENV_ROOT="/usr/local/var/pyenv/"' >> /etc/profile""",
            """grep "pyenv init" /etc/profile || echo 'eval "$(pyenv init -)"' >> /etc/profile""",
            """grep "pyenv virtualenv" /etc/profile || echo 'eval "$(pyenv virtualenv-init -)"' >> /etc/profile""",
        ]

        if remote_os == 'mac':
            command_list = ["sudo sh -c '%s'" % shell_quote(v) for v in command_list]
            pass

        for cmd in command_list:
            run(cmd)
            pass

        pass

    def install_node(self, root, pkgs_config):
        """
        global node package denends

        ..note::

            this will install global package.

        :param root: pkgs_config root directory path
        :param pkgs_config: package.json pkgs_config

        :return:
        """

        pkg = pkgs_config.get('node')
        if not pkg:
            return

        def on_centos():
            mirror_put(root, '/etc/yum.repos.d', validate=False)
            run('yum install -y node npm')
            pass

        def on_mac():
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
            * finish

        :param options:
        :return:
        """

        package_root, config_root, fabric_root = get_roots(options.dir)
        bind_hosts(fabric_root, options.env)

        # try upload repo config if it can recognize
        using_config = os.path.join(config_root, options.env)
        try:
            packages_config = json.load(open(os.path.join(package_root, options.env, 'packages.json'), 'r'))
        except ValueError:
            self.error("Invalid json syntax:%s" % os.path.join(package_root, options.env, 'packages.json'))

        execute_list = []

        if not options.skip_pyenv:
            execute_list.append(lambda: self.install_pyenv())

        if not options.skip_pkg:
            execute_list.append(lambda: self.install_package(using_config, packages_config))

        if not options.skip_node:
            execute_list.append(lambda: self.install_node(using_config, packages_config))

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
            (('--skip-pkg',), dict(action='store_true', help='skip install pkg', )),
            (('--skip-pyenv',), dict(action='store_true', help='skip install pyenv', )),
            (('--skip-node',), dict(action='store_true', help='skip install node', )),
        ]
        pass

    pass
