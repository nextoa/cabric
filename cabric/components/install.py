# -*- coding: utf-8 -*-

import os
import sys
import json
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute


class InstallComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    def install_yum(self, root, pkg_list):
        mirror_put(root, '/etc/yum.repos.d', validate=False)
        run('yum install -y {}'.format(' '.join(pkg_list)))
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
        packages_config = json.load(open(os.path.join(package_root, options.env, 'packages.json'), 'r'))


        def hi():
            run('echo hello')
            pass

        execute([hi])
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
