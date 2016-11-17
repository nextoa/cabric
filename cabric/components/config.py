# -*- coding: utf-8 -*-

import os
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform, run_block

try:
    from shlex import quote as shell_quote
except ImportError:
    from pipes import quote as shell_quote


class ConfigComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    def run(self, options):
        """
        plan feature

            use rsync instead fabric put.
            but rsync will may cause permission errors.
            we should fix this.

        :param options:
        :return:
        """

        package_root, config_root, fabric_root = get_roots(options.dir)
        bind_hosts(fabric_root, options.env)

        # try upload repo config if it can recognize
        using_config = os.path.join(config_root, options.env)

        mirror_put(using_config, '/')
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return []

    pass
