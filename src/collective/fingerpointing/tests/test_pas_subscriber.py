# -*- coding: utf-8 -*-
"""Tests for lifecycle subscriber."""
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import QIBBB
from logging import INFO
from Products.PlonePAS.events import UserLoggedInEvent
from Products.PlonePAS.events import UserLoggedOutEvent
from Products.PluggableAuthService.events import GroupDeleted
from Products.PluggableAuthService.events import PrincipalCreated
from Products.PluggableAuthService.events import PrincipalDeleted
from testfixtures import LogCapture
from zope.event import notify

import unittest


class PasSubscribersTestCase(unittest.TestCase, QIBBB):
    """Tests for PluggableAuthService subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_user_login(self):
        event = UserLoggedInEvent(self.request)
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=login '),  # noqa: E501
            )

    def test_user_logout(self):
        event = UserLoggedOutEvent(self.request)
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=logout '),  # noqa: E501
            )

    def test_user_created(self):
        event = PrincipalCreated('foo')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create principal=foo'),  # noqa: E501
            )

    def test_user_removed(self):
        event = PrincipalDeleted('foo')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove user=foo'),  # noqa: E501
            )

    def test_group_removed(self):
        event = GroupDeleted('bar')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove group=bar'),  # noqa: E501
            )

    def test_susbcriber_ignored_when_package_not_installed(self):
        # authentication events should not raise errors
        # if package is not installed
        self.uninstall()  # BBB: QI compatibility

        event = UserLoggedInEvent(self.request)
        notify(event)
        event = UserLoggedOutEvent(self.request)
        notify(event)
        event = PrincipalCreated('foo')
        notify(event)
        event = PrincipalDeleted('foo')
        notify(event)
