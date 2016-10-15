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

        if options.register is True:
            os.system('python setup.py register -r %s' % repo)
            pass

        os.system('python setup.py sdist upload -r %s' % repo)
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('--register', '-r'), dict(action='store_true', help='register package to repo.')),
            (('--source', '-s'), dict(default='cabric', help='try load private repo.', )),
            (('--public',), dict(action='store_true', help='upload to pypi repo.')),
        ]
        pass

    pass
