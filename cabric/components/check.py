# -*- coding: utf-8 -*-

from cliez.component import Component

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
