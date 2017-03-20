# -*- coding: utf-8 -*-

import os

from cliez.component import Component


class CleanComponent(Component):
    # un-comment this can disable global options
    # exclude_global_option = True

    def run(self, options):
        for v in os.walk(options.dir):
            for base_name in v[2]:
                if base_name.endswith('.pyc') or base_name.endswith('.pyo'):
                    file_name = os.path.join(v[0], base_name)
                    os.unlink(file_name)
                    self.logger.debug("delete file:%s" % file_name)
                    pass
                pass

            dir_name = os.path.basename(v[0])

            if dir_name == '__pycache__':
                try:
                    os.rmdir(v[0])
                    self.logger.debug("delete directory:%s" % v[0])
                except OSError:
                    self.warn_message(
                        "can't delete %s cache directory." % v[0])
                    pass
                pass
            pass

        pass

    pass
