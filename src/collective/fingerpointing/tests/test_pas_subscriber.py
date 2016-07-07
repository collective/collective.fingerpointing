# -*- coding: utf-8 -*-
"""Tests for lifecycle subscriber."""
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.testing import INTEGRATION_TESTING
from logging import INFO
from plone import api
from Products.PlonePAS.events import UserLoggedInEvent
from Products.PlonePAS.events import UserLoggedOutEvent
from Products.PluggableAuthService.events import GroupDeleted
from Products.PluggableAuthService.events import PrincipalCreated
from Products.PluggableAuthService.events import PrincipalDeleted
from testfixtures import LogCapture
from zope.event import notify

import unittest


class PasSubscribersTestCase(unittest.TestCase):

    """Tests for PluggableAuthService subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']

    def test_user_login(self):
        event = UserLoggedInEvent(self.request)
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=login '),
            )

    def test_user_logout(self):
        event = UserLoggedOutEvent(self.request)
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=logout '),
            )

    def test_user_created(self):
        event = PrincipalCreated('foo')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=create principal=foo'),
            )

    def test_user_removed(self):
        event = PrincipalDeleted('foo')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=remove user=foo'),
            )

    def test_group_removed(self):
        event = GroupDeleted('bar')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=remove group=bar'),
            )

    def test_susbcriber_ignored_when_package_not_installed(self):
        # authentication events should not raise errors
        # if package is not installed
        portal = self.layer['portal']
        qi = portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])

        event = UserLoggedInEvent(self.request)
        notify(event)
        event = UserLoggedOutEvent(self.request)
        notify(event)
        event = PrincipalCreated('foo')
        notify(event)
        event = PrincipalDeleted('foo')
        notify(event)
