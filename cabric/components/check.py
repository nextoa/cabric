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


class CheckComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True


    def run(self, options):
        """
        plan feature

        we should check

        * only support centos or macosx
        * check pssh is installed
        * check prsync is installed
        * check brew is installed

        :param options:
        :return:
        """



        pass


    pass
