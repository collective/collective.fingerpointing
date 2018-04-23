# -*- coding: utf-8 -*-
"""Tests for iterate subscribers.

Dexterity content types have different names.
"""
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import IS_PLONE_5
from collective.fingerpointing.testing import QIBBB
from logging import INFO
from plone import api
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from testfixtures import LogCapture

import unittest


class IterateSubscribersTestCase(unittest.TestCase, QIBBB):
    """Tests for plone.app.iterate subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self._disable_lifecycle_events()

        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')
        self.doc = api.content.create(self.folder, 'Document', 'doc')

    def _disable_lifecycle_events(self):
        name = IFingerPointingSettings.__identifier__ + '.audit_lifecycle'
        api.portal.set_registry_record(name, value=False)

    def test_checkout_checkin(self):
        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=checkout object=<Document at doc> working_copy=<Document at copy_of_doc>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=checkin object=<Document at copy_of_doc> baseline=<Document at doc>'),  # noqa: E501
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=checkout object=<ATDocument at doc> working_copy=<ATDocument at copy_of_doc>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=checkin object=<ATDocument at copy_of_doc> baseline=<ATDocument at doc>'),  # noqa: E501
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            wc = ICheckinCheckoutPolicy(self.doc).checkout(self.folder)
            self.doc = ICheckinCheckoutPolicy(wc).checkin('updated')
            log.check(*expected)

    def test_checkout_cancel(self):
        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=checkout object=<Document at doc> working_copy=<Document at copy_of_doc>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=cancel checkout object=<Document at copy_of_doc> baseline=<Document at doc>'),  # noqa: E501
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=checkout object=<ATDocument at doc> working_copy=<ATDocument at copy_of_doc>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=cancel checkout object=<ATDocument at copy_of_doc> baseline=<ATDocument at doc>'),  # noqa: E501
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            wc = ICheckinCheckoutPolicy(self.doc).checkout(self.folder)
            ICheckinCheckoutPolicy(wc).cancelCheckout()
            log.check(*expected)

    def test_susbcriber_ignored_when_package_not_installed(self):
        # iterate events should not raise errors if package not installed
        self.uninstall()  # BBB: QI compatibility

        wc = ICheckinCheckoutPolicy(self.doc).checkout(self.folder)
        ICheckinCheckoutPolicy(wc).cancelCheckout()
