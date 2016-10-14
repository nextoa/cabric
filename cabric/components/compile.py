# -*- coding: utf-8 -*-

import os
import sys
import py_compile

from cliez.component import Component


class CompileComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    def run(self, options):
        """

        :param options:
        :return:
        """
        tag = 'o' if options.optimize == 2 else 'c'

        for v in os.walk(options.dir):
            for base_name in v[2]:
                if not base_name.endswith('.py'):
                    continue
                file_name = os.path.join(v[0], base_name)

                kwargs = {
                    'optimize': 2
                }

                if sys.version > (3, 2):
                    kwargs = {
                        'optimize': options.optimize
                    }
                    pass

                py_compile.compile(file_name, cfile=file_name + tag, **kwargs)

                self.logger.debug('compile file %s' % file_name)
                pass
            pass
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('--keep-document',), dict(help='use set optimize to 1', )),
            (('--original',), dict(help='use set optimize to 1', )),
        ]
        pass

    pass
