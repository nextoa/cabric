# -*- coding: utf-8 -*-

import os
import unittest
import argparse
from cliez import parser


class CompileComponentTests(unittest.TestCase):
    def setUp(self):
        from cabric import main
        pass

    def test_ok(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'compile',
                                                      '--debug',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_optimize(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'compile', '-OO',
                                                      '--debug',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    pass
