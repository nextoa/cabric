# -*- coding: utf-8 -*-

import os
import sys
import json
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform


class InstallComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    system_python_version = '2.7.12'

    def install_package(self, root, pkgs_config):
        """
        install system package

        :param root: pkgs_config root directory path
        :param pkgs_config: package.json pkgs_config
        :return:
        """

        remote_os = get_platform()

        if remote_os == 'centos':
            pkg = pkgs_config.get('yum')
            if not pkg:
                return

            mirror_put(root, '/etc/yum.repos.d', validate=False)
            run('yum install -y {}'.format(' '.join(pkg)))
            pass
        elif remote_os == 'mac':
            pkg = pkgs_config.get('brew')
            if not pkg:
                return
            run('brew install {}'.format(' '.join(pkg)))
            pass
        else:
            raise NotImplemented("not support platform.")

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
            run('ln -sv /usr/local/var/pyenv/bin/pyenv /usr/local/bin/pyenv')
            pass
        elif remote_os == 'mac':
            run('brew install git pyenv')
            pass

        run('export PYENV_ROOT="/usr/local/var/pyenv/" && eval "$(pyenv init -)"')
        # run('eval "$(pyenv virtualenv-init -)"')
        run('export PYENV_ROOT="/usr/local/var/pyenv/" && pyenv install %s' % self.system_python_version)
        pass

    def install_pypi(self, root, pkgs_config, upgrade=False):
        """
        pip depends

        pip package will install from two source location.

            * requirement.txt in `options.dir`
            * 'pypi' key-node from packages.json

        :param root: pkgs_config root directory path
        :param pkgs_config: package.json pkgs_config

        :return:
        """

        version_file = os.path.join(self.options.dir, '.python-version')

        if os.path.exists(version_file):
            versions_buffer = run('pyenv whence python')
            python_versions = versions_buffer.strip().split("\r\n")
            python_version = open(version_file, 'r').readline().strip()

            if python_version not in python_versions:
                run('pyenv install %s' % python_version)

            pass

        requirements_file = os.path.join(self.options.dir, 'requirements.txt')

        if os.path.exists(requirements_file):
            with open(requirements_file, 'r') as fp:
                for pkg in fp:
                    if pkg.strip().find('#') != 0:
                        run('pip install %s' % pkg)
                    pass
            pass

        run('pip install {}'.format(' '.join(pkg)))
        pass

    def install_node(self, root, pkgs_config):
        """
        global node package denends

        :param root: pkgs_config root directory path
        :param pkgs_config: package.json pkgs_config

        :return:
        """

        pkg = pkgs_config.get('node')
        if not pkg:
            return

        run('node install -g {}'.format(' '.join(pkg)))
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

        execute([
            # depends install
            # lambda: self.install_pyenv(using_config),

            # user install
            # lambda: self.install_package(using_config, packages_config),
            lambda: self.install_pypi(using_config, packages_config),
            # lambda: self.install_node(using_config, packages_config),
        ])
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('--node', '-p'), dict(nargs='+', help='install sub node settings', )),
        ]
        pass

    pass
