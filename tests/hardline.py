# -*- coding: utf-8 -*-

from __future__ import absolute_import
import argparse
import unittest

from cliez import parser



class HardlineComponentTests(unittest.TestCase):

    def setUp(self):
        from cabric import main
        pass

    # def test_ok(self):
    #     with self.assertRaises(OSError):
    #         parser.parse(argparse.ArgumentParser(),
    #                      argv=['command', 'hardline',
    #                            'normal',
    #                            '--dir',
    #                            __file__.rsplit('/', 2)[
    #                                0]])
    #
    #     pass

    def test_list(self):
        parser.parse(argparse.ArgumentParser(),
                     argv=['command', 'hardline',
                           '--list',
                           '--dir',
                           __file__.rsplit('/', 2)[
                               0]])

        pass


    def test_workflow(self):
        parser.parse(argparse.ArgumentParser(),
                     argv=['command', 'hardline',
                           'normal',
                           '--preview',
                           '--dir',
                           __file__.rsplit('/', 2)[
                               0]])

        pass

    pass
