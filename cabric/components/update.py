# -*- coding: utf-8 -*-

import os
import sys
import json
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform, run_block


class UpdateComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    def run(self, options):
        """
        :param options:
        :return:
        """

        self.print_message("plan feature")
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
