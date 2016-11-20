# -*- coding: utf-8 -*-

import os
import sys
import json
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform


class DeployComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    def run(self, options):
        """
        workflow
            * upload deploy-key when not exist.
            * git clone with project-deploy-key.
            * install requirements.txt package if exist
            * install nodejs local-package if exist
            * parse template file
            * git pull or checkout commit
            * add crontab if user set
            * finish

        :param options:
        :return:
        """

        # package_root, config_root, fabric_root = get_roots(options.dir)
        # bind_hosts(fabric_root, options.env)
        #
        # # try upload repo config if it can recognize
        # using_config = os.path.join(config_root, options.env)
        # try:
        #     packages_config = json.load(open(os.path.join(package_root, options.env, 'packages.json'), 'r'))
        # except ValueError:
        #     self.error("Invalid json syntax:%s" % os.path.join(package_root, options.env, 'packages.json'))
        #
        # execute([
        #     # depends install
        #     # lambda: self.install_pyenv(using_config),
        #
        #     # user install
        #     # lambda: self.install_package(using_config, packages_config),
        #     lambda: self.install_pypi(using_config, packages_config),
        #     # lambda: self.install_node(using_config, packages_config),
        # ])
        pass

    @classmethod
    def add_arguments(cls):
        """
        python web project deploy tool
        """
        return [
            ('commit', dict(nargs='?', help='set which commit to deploy,default is latest version', )),
            (('--skip-enable-service',), dict(action='store_true', help='skip enable system service', )),
            (('--skip-requirements',), dict(action='store_true', help='skip install requirements', )),
            (('--skip-compile-template',), dict(action='store_true', help='skip compile template', )),
            (('--skip-upload-resource',), dict(action='store_true', help='skip upload resource', )),
        ]
        pass

    pass
