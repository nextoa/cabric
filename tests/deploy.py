# -*- coding: utf-8 -*-

import os
import unittest
import argparse
import shutil
from cliez import parser


class DeployComponentTests(unittest.TestCase):



    def setUp(self):
        from cabric import main

        test_key = os.path.expanduser('~/.ssh/cabric.rsa')

        if os.path.exists(test_key):
            os.unlink(test_key)

        pass

    def test_invalid_env(self):
        with self.assertRaises(OSError):
            parser.parse(argparse.ArgumentParser(), argv=['command', 'deploy',
                                                          '--debug',
                                                          '--env', 'invalid-env',
                                                          '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_upload_key(self):
        """
        ..note::
            github token must be valid

        :return:
        """

        parser.parse(argparse.ArgumentParser(), argv=['command', 'deploy',
                                                      '--debug',
                                                      '--env', 'beta',
                                                      '--skip-enable-services',
                                                      '--skip-requirements',
                                                      '--skip-compile-templates',
                                                      '--skip-upload-resources',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass


    pass
