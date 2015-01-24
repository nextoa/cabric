# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import bree
import bree.web
from bree.testing import active_ci

from tornado.testing import AsyncTestCase, gen_test
from demo import settings
from demo import config


class TestCase(AsyncTestCase):
    @gen_test(timeout=3)
    @active_ci(settings.pro, settings.ci, __file__)
    def testNormal(self):

        pass

    pass




