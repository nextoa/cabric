# -*- coding: utf-8 -*-

import os
from cliez.component import Component


class PackageComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    def run(self, options):

        if options.public:
            repo = 'pypi'
            pass
        else:
            repo = options.source
            pass

        os.system('python setup.py sdist upload -r %s' % repo)
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('--source', '-s'), dict(help='try load repo local path.', )),
            (('--public',), dict(action='store_true', help='upload to pypi repo.')),
        ]
        pass

    pass
