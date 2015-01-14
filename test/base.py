# -*- coding: utf-8 -*-


import unittest

import os


class BaseUnitTest(unittest.TestCase):
    def testBase(self):


        root = '../config/fabez'
        files = os.listdir('../config/fabez')

        routes = {}

        for f in files:

            if f.endswith('conf'):
                k = f.rsplit('.')[0]
                v = os.path.join(root, f)

                routes[k] = v
                pass

            pass


        pass

    pass