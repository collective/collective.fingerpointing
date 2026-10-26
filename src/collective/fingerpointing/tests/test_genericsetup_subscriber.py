"""Tests for Generic Setup subscriber."""
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.testing import INTEGRATION_TESTING
from logging import INFO
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.utils import get_installer
from testfixtures import LogCapture

import unittest


ADD_ON = 'plone.session'


class GenericSetupSubscribersTestCase(unittest.TestCase):
    """Tests Generic Setup subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.setup_tool = self.portal['portal_setup']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # disable registry audit
        name = IFingerPointingSettings.__identifier__ + '.audit_registry'
        api.portal.set_registry_record(name, False)

    @property
    def qi(self):
        return get_installer(self.portal, self.request)

    def test_profile_imports(self):
        version = self.setup_tool.getVersionForProfile('plone.session:default')
        expected = (
            ('collective.fingerpointing', 'INFO', f'user=test_user_1_ ip=None action=profile imported id=plone.session:default version={version}'),  # noqa: E501
            ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=profile imported id=plone.session:uninstall version=-'),  # noqa: E501
        )
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.qi.install_product(ADD_ON)
            self.qi.uninstall_product(ADD_ON)
            log.check(*expected)

    def test_susbcriber_ignored_when_package_not_installed(self):
        # events should not raise errors if package is not installed
        self.qi.uninstall_product(PROJECTNAME)
        self.qi.install_product(ADD_ON)
        self.qi.uninstall_product(ADD_ON)
