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

        self.logger.debug("api-auth with key: %s,%s", key,
                          secret[0:2] + '*' * 10 + secret[-2:])

        if None in [zone, key, secret]:
            raise ValueError(
                "Please set `QINGCLOUD_ACCESS_KEY',`QINGCLOUD_ACCESS_SECRET',"
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

        def wrapper(*args, **kwargs):
            return getattr(self.connector, name)(*args, **kwargs)

        if hasattr(self.connector, name) and callable(
                getattr(self.connector, name)):
            return wrapper

        raise AttributeError(name)

    _create_rules = [
        # device_type,describe api,create api,modify api
        ('loadbalancer', '',),
        ('loadbalancer-policy', '',),
    ]

    def create(self, device_type, name, arg_list=[], arg_dict={},
               overwrite=False):
        """
        create device

        :param device_type:
        :param name:
        :param overwrite:
        :return:
        """

        for rule in self._create_rules:

            if device_type == rule[0]:
                method = getattr(self.client, rule[1])

                pass

            pass

        pass

    def get_loadbalancer_policy(self, name):
        """
        try get loadbalancer policy device by name.
        :param policy_name:
        :return: policy dict, if not exist, raise ValueError
        """

        policies = self.connector.describe_loadbalancer_policies()
        pos_name_set = [(k, v['loadbalancer_policy_name']) for k, v in
                        enumerate(policies['loadbalancer_policy_set'])]
        pos_set, name_set = zip(*pos_name_set)

        try:
            pos = pos_set[name_set.index(name)]
            policy = policies['loadbalancer_policy_set'][pos]
        except (ValueError, IndexError):
            raise ValueError("%s not exist" % name)

        return policy

    def get_or_create_loadbalancer_policy(self, policy_name, *args, **kwargs):
        """

        :param policy_name:
        :param overwrite:
        :return:
        """

        try:
            policy = self.get_loadbalancer_policy(policy_name)
        except ValueError:
            self.connector.create_loadbalancer_policy(policy_name, *args,
                                                      **kwargs)
            policy = self.get_loadbalancer_policy(policy_name)
            pass
        return policy

    def get_loadbalancer_policy_rule(self, policy_id, name):
        """
        try get loadbalancer policy rule by name.
        :param policy_id: policy id
        :param name: rule name
        :return: dict, if not exist, raise ValueError
        """
        rules = self.connector.describe_loadbalancer_policy_rules(
            loadbalancer_policy=policy_id)

        pos_name_set = [(k, v['loadbalancer_policy_rule_name']) for k, v in
                        enumerate(rules['loadbalancer_policy_rule_set'])]
        pos_set, name_set = zip(*pos_name_set)

        try:
            pos = pos_set[name_set.index(name)]
            rule = rules['loadbalancer_policy_rule_set'][pos]
        except (ValueError, IndexError):
            raise ValueError("%s not exist" % name)

        return rule

    def get_or_add_loadbalancer_policy_rules(self, policy_id, rule, *args,
                                             **kwargs):
        try:
            rule = self.get_loadbalancer_policy_rule(policy_id, rule[
                'loadbalancer_policy_rule_name'])
        except ValueError:
            self.connector.add_loadbalancer_policy_rules(policy_id, [rule],
                                                         *args, **kwargs)
            rule = self.get_loadbalancer_policy_rule(policy_id, rule[
                'loadbalancer_policy_rule_name'])
            pass

        return rule

    def get_loadbalancer_backend(self, listener_id, name):
        """
        try get load balancer backend
        :param policy_name:
        :return: policy dict, if not exist, raise ValueError
        """

        backends = self.connector.describe_loadbalancer_backends(
            loadbalancer_listener=listener_id)
        pos_name_set = [(k, v['loadbalancer_backend_name']) for k, v in
                        enumerate(backends['loadbalancer_backend_set'])]

        try:
            pos_set, name_set = zip(*pos_name_set)
            pos = pos_set[name_set.index(name)]
            backend = backends['loadbalancer_backend_set'][pos]
        except (ValueError, IndexError):
            raise ValueError("%s not exist" % name)

        return backend

    def get_or_add_load_balancer_backends(self, loadbalancer_listener, backend,
                                          *args, **kwargs):
        try:
            backend = self.get_loadbalancer_backend(
                loadbalancer_listener,
                backend[
                    'loadbalancer_backend_name'])
        except ValueError:
            self.connector.add_backends_to_listener(
                loadbalancer_listener,
                [backend], *args, **kwargs)
            backend = self.get_loadbalancer_backend(
                loadbalancer_listener,
                backend[
                    'loadbalancer_backend_name'])
            pass

        return backend

    # def get_or_create_server_certicifate(self, loadbalancer_listener,
    #                                      backend,
    #                                      *args, **kwargs):
    #     try:
    #         backend = self.get_loadbalancer_backend(
    #             loadbalancer_listener,
    #             backend[
    #                 'loadbalancer_backend_name'])
    #     except ValueError:
    #         self.connector.add_backends_to_listener(
    #             loadbalancer_listener,
    #             [backend], *args, **kwargs)
    #         backend = self.get_loadbalancer_backend(
    #             loadbalancer_listener,
    #             backend[
    #                 'loadbalancer_backend_name'])
    #         pass
    #
    #     return backend
    pass
