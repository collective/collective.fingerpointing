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

    def test_get_audit_log_files(self):
        audit_log_files = self.view._get_audit_log_files
        # we have at least one log file to process
        self.assertGreaterEqual(len(audit_log_files), 1)
        # the first file is the current audit log
        self.assertEqual('./audit.log', audit_log_files[0])

    def test_log_tail(self):
        from Products.PlonePAS.events import UserLoggedOutEvent
        from zope.event import notify
        event = UserLoggedOutEvent(self.request)
        notify(event)
        audit_log = self.view.get_audit_log.split('\n')
        # user logged out event is first on log (newer entries first)
        self.assertIn('user=test ip=127.0.0.1 action=logout', audit_log[0])
