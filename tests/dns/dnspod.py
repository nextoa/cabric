# -*- coding: utf-8 -*-

import logging
import unittest

from cabric.dns.dnspod import DNSPod


class DnspodTestCase(unittest.TestCase):
    """
    please set os.environment.DNSPOD_LOGIN_TOKEN value
    """

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.client = DNSPod()
        self.drop_config = []
        pass

    def tearDown(self):
        if self.drop_config:
            for c in self.drop_config:
                self.client.remove_record(c)
                pass

        if self.client.domain:
            self.assertNotEqual(None, self.client.remove_domain())
        pass

    def test_api_version(self):
        self.assertIsInstance(float(self.client.get_version()), float)
        pass

    def test_bind_domain(self):
        self.assertEqual(True, self.client.bind_domain('kay8.com'))
        pass

    def test_bind_domain02(self):
        self.client = DNSPod(domain='kay8.com')
        self.assertEqual(True, self.client.bind_domain())
        pass

    def test_bind_record(self):
        self.test_bind_domain()

        self.drop_config = [
            dict(value='1.1.1.1', record_type='A', sub_domain='unittest-01'),
            dict(value='1.1.1.2', record_type='A', sub_domain='unittest-01', active=False)
        ]

        [self.assertNotEqual(None, self.client.bind_record(v)) for v in self.drop_config]
        pass

    def test_bind_record02(self):
        self.test_bind_domain()

        self.drop_config = [
            dict(value='1.1.1.1', record_type='A', sub_domain='unittest-02', record_line='电信'),
            dict(value='1.1.1.2', record_type='A', sub_domain='unittest-02', record_line='移动')
        ]

        [self.assertNotEqual(None, self.client.bind_record(v)) for v in self.drop_config]
        pass

    def test_bind_record03(self):
        self.test_bind_domain()

        self.drop_config = [
            dict(value='1.1.1.1', record_type='A', sub_domain='unittest-01'),
            dict(value='1.1.1.2', record_type='A', sub_domain='unittest-01', active=False)
        ]

        [self.assertNotEqual("1", self.client.bind_record(v)['status']['code']) for v in self.drop_config]
        [self.assertNotEqual("104", self.client.bind_record(v)['status']['code']) for v in self.drop_config]
        pass

    def test_get_record_id(self, test_data=None):
        test_data = test_data or {
            "value": "1.1.1.2",
            "sub_domain": "unittest-02",
            "record_type": "A",
            "record_line": "电信",
        }

        self.test_bind_record02()
        record_id = self.client.get_record_id(test_data)
        self.assertNotEqual(None, record_id)

        return record_id

    def test_modify(self):
        test_data = {
            "value": "2.2.2.2",
            "sub_domain": "unittest-02",
            "record_type": "A",
            "record_line": "电信",
            "status": "disable",
        }

        record_id = self.test_get_record_id()
        self.assertNotEqual(None, self.client.modify_record(record_id, test_data))
        pass

    pass
