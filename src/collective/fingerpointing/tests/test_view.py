# -*- coding: utf-8 -*-
from collective.fingerpointing.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import logout

import unittest


class LogViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.view = api.content.get_view(
            'fingerpointing-audit-log', self.portal, self.request)

    def test_audit_log_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@fingerpointing-audit-log')

    def test_available(self):
        self.assertTrue(self.view.available)
