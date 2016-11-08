# -*- coding: utf-8 -*-

import os
import sys
import json
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform


class InstallComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    def install_package(self, root, config):
        """

        :param root: config root directory path
        :param config: package.json config
        :return:
        """

        remote_os = get_platform()

        if remote_os == 'centos':
            pkg = config.get('yum')
            if not pkg:
                return

            mirror_put(root, '/etc/yum.repos.d', validate=False)
            run('yum install -y {}'.format(' '.join(pkg)))
            pass
        elif remote_os == 'mac':
            pkg = config.get('brew')
            if not pkg:
                return
            run('brew install {}'.format(' '.join(pkg)))
            pass
        else:
            raise NotImplemented("not support platform.")

        pass

    def install_pypi(self):
        pass

    def install_node(self):
        pass

    def install_brew(self):
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
            lambda: self.install_package(using_config, packages_config)
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
