# -*- coding: utf-8 -*-
from collective.fingerpointing.testing import INTEGRATION_TESTING
from logging import INFO
from testfixtures import LogCapture
from zope.event import notify

import unittest


class PasSubscribersTestCase(unittest.TestCase):

    """Tests for PluggableAuthService subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']

    def test_user_login(self):
        from Products.PlonePAS.events import UserLoggedInEvent
        event = UserLoggedInEvent(self.request)
        with LogCapture(level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=logged in '),
            )

    def test_user_logout(self):
        from Products.PlonePAS.events import UserLoggedOutEvent
        event = UserLoggedOutEvent(self.request)
        with LogCapture(level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=logged out '),
            )

    def test_user_created(self):
        from Products.PluggableAuthService.events import PrincipalCreated
        event = PrincipalCreated('foo')
        with LogCapture(level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=user created object=foo'),
            )

    def test_user_removed(self):
        from Products.PluggableAuthService.events import PrincipalDeleted
        event = PrincipalDeleted('foo')
        with LogCapture(level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=user removed object=foo'),
            )
