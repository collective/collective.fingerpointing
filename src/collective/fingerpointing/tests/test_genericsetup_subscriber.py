# -*- coding: utf-8 -*-
"""Tests for Generic Setup subscriber."""
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import IS_BBB
from collective.fingerpointing.testing import IS_PLONE_6
from logging import INFO
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from testfixtures import LogCapture

import unittest


ADD_ON = 'plone.session'


class GenericSetupSubscribersTestCase(unittest.TestCase):
    """Tests Generic Setup subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # disable registry audit
        name = IFingerPointingSettings.__identifier__ + '.audit_registry'
        api.portal.set_registry_record(name, False)

    @property
    def qi(self):
        if IS_BBB:  # Plone 4.3
            return self.portal['portal_quickinstaller']
        else:
            from Products.CMFPlone.utils import get_installer
            return get_installer(self.portal, self.request)

    @unittest.skipIf(IS_BBB, 'Plone >= 5.1')
    def test_profile_imports(self):
        if IS_PLONE_6:
            version = 1002
        else:
            version = 1001
        expected = (
            ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=profile imported id=plone.session:default version={}'.format(version)),  # noqa: E501
            ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=profile imported id=plone.session:uninstall version=-'),  # noqa: E501
        )
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.qi.install_product(ADD_ON)
            self.qi.uninstall_product(ADD_ON)
            log.check(*expected)

    @unittest.skipUnless(IS_BBB, 'Plone 4.3')
    def test_profile_imports_BBB(self):
        expected = (
            ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=profile imported id=plone.session:default version=1000'),  # noqa: E501
        )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.qi.installProduct(ADD_ON)
            self.qi.uninstallProducts([ADD_ON])
            log.check(*expected)

    @unittest.skipIf(IS_BBB, 'Plone >= 5.1')
    def test_susbcriber_ignored_when_package_not_installed(self):
        # events should not raise errors if package is not installed
        self.qi.uninstall_product(PROJECTNAME)
        self.qi.install_product(ADD_ON)
        self.qi.uninstall_product(ADD_ON)

    @unittest.skipUnless(IS_BBB, 'Plone 4.3')
    def test_susbcriber_ignored_when_package_not_installed_BBB(self):
        # events should not raise errors if package is not installed
        self.qi.uninstallProducts([PROJECTNAME])
        self.qi.installProduct(ADD_ON)
        self.qi.uninstallProducts([ADD_ON])
