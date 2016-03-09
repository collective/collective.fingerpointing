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

    def test_audit_log_view(self):
        view = self.view.__of__(self.portal)
        self.assertTrue(view())

    def test_audit_log_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@fingerpointing-audit-log')

    def test_log_tail(self):
        from logging import INFO
        from Products.PlonePAS.events import UserLoggedOutEvent
        from testfixtures import LogCapture
        from zope.event import notify
        # verify user logged out event is the last on the log
        event = UserLoggedOutEvent(self.request)
        with LogCapture(level=INFO):
            notify(event)
            self.assertIn('action=logged out', self.view.log_tail[-1])
