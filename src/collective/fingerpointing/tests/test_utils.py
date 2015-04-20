# -*- coding: utf-8 -*-
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.utils import get_request_information
from plone.app.testing import TEST_USER_NAME

import unittest


class UtilsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def test_get_request_information(self):
        request = self.layer['request']
        request['AUTHENTICATED_USER'] = TEST_USER_NAME
        request['REMOTE_ADDR'] = localhost = '127.0.0.1'
        self.assertEqual(
            get_request_information(),
            (TEST_USER_NAME, localhost),
        )
