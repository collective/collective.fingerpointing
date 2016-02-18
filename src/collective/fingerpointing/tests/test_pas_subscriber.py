# -*- coding: utf-8 -*-
"""Tests for lifecycle subscriber.

Log output is slightly different among Plone 4 and Plone 5.
"""
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import PLONE_VERSION
from logging import INFO
from plone import api
from Products.PlonePAS.events import UserLoggedInEvent
from Products.PlonePAS.events import UserLoggedOutEvent
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
        if PLONE_VERSION >= '5.0':
            expected = (
                ('plone.protect', 'INFO', 'auto rotating keyring _system'),
                ('plone.protect', 'INFO', 'auto rotating keyring _forms'),
                ('plone.protect', 'INFO', 'auto rotating keyring _anon'),
                ('plone.protect', 'INFO', 'auto rotating keyring _system'),
                ('plone.protect', 'INFO', 'auto rotating keyring _forms'),
                ('plone.protect', 'INFO', 'auto rotating keyring _anon'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=logged in '),
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=logged in '),
            )

        event = UserLoggedInEvent(self.request)
        with LogCapture(level=INFO) as log:
            notify(event)
            log.check(*expected)

    def test_user_logout(self):
        event = UserLoggedOutEvent(self.request)
        with LogCapture(level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=logged out '),
            )

    def test_user_created(self):
        event = PrincipalCreated('foo')
        with LogCapture(level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=user created object=foo'),
            )

    def test_user_removed(self):
        event = PrincipalDeleted('foo')
        with LogCapture(level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=user removed object=foo'),
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
