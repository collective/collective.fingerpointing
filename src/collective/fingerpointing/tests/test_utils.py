# -*- coding: utf-8 -*-
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.utils import get_request_information

import unittest


class UtilsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']

    def test_get_request_information(self):
        self.assertEqual(
            get_request_information(), ('test_user_1_', 'None'))

    def test_get_request_information_anonymous(self):
        from plone.app.testing import logout
        logout()
        self.assertEqual(get_request_information(), ('-', 'None'))

    def test_get_request_information_cloudflare(self):
        self.request.environ['HTTP_CF_CONNECTING_IP'] = '192.168.1.1'
        self.assertEqual(
            get_request_information(), ('test_user_1_', '192.168.1.1'))
