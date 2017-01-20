# -*- coding: utf-8 -*-


from __future__ import absolute_import

import logging
import os

logger = logging.getLogger(__name__)


class QingCloud(object):
    """
    Wrapper for official qingcloud package
    """

    connector = None

    def __init__(self, zone=None):
        super(QingCloud, self).__init__()
        self.zone = zone
        self.logger = logger
        pass

    def connect(self, zone=None):
        """
        :return:
        """
        import qingcloud.iaas

        zone = zone or self.zone

        key = os.environ.get("QINGCLOUD_ACCESS_KEY")
        secret = os.environ.get("QINGCLOUD_ACCESS_SECRET")

        self.logger.debug("api-auth with key: %s,%s", key, secret[0:2] + '*' * 10 + secret[-2:])

        if None in [zone, key, secret]:
            raise ValueError("Please set `QINGCLOUD_ACCESS_KEY',`QINGCLOUD_ACCESS_SECRET',"
                             "and make sure `zone' has set")

        self.connector = qingcloud.iaas.connect_to_zone(
            zone,
            key,
            secret
        )

    def __getattr__(self, name):
        """
        wrapper for qingcloud
        :param name:
        :return:
        """
        if hasattr(self.connector, name) and callable(getattr(self.connector, name)):
            def wrapper(*args, **kwargs):
                return getattr(self.connector, name)(*args, **kwargs)

            return wrapper
        raise AttributeError(name)

    pass
