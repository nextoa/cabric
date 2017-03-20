# -*- coding: utf-8 -*-

from cliez.component import Component


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
            (('--node', '-p'),
             dict(nargs='+', help='install sub node settings', )),
        ]
        pass

    pass
