# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import unittest

from cabric.cloud.qingcloud import QingCloud

logging.basicConfig(level=logging.DEBUG)


class QingCloudTestCase(unittest.TestCase):
    """
    please set os.environment. value
    """

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.client = QingCloud()
        self.drop_config = []
        pass

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(None, self.client.connector)
        pass

    def test_connector(self):
        """
        Don't forget set os.env['QINGCLOUD_ACCESS_KEY'] and os.env['QINGCLOUD_ACCESS_SECRET']
        :return:
        """
        self.client.connect('pek-2')
        self.assertNotEqual(None, self.client.connector)
        pass

    def test_api(self):
        """
        Don't forget set os.env['QINGCLOUD_ACCESS_KEY'] and os.env['QINGCLOUD_ACCESS_SECRET']
        :return:
        """

        self.client.connect('pek2')
        result = self.client.describe_instances()
        self.assertEqual(0, result.get('ret_code', -1))
        pass

    pass
