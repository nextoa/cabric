# -*- coding: utf-8 -*-

import argparse
import unittest

from cliez import parser


class CleanComponentTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_ok(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'clean',
                                                      '--debug',
                                                      '--dir',
                                                      __file__.rsplit('/', 2)[
                                                          0]])
        pass

    pass
