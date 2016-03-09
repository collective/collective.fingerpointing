# -*- coding: utf-8 -*-
"""Ensure add-on is properly installed and uninstalled."""
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.interfaces import IBrowserLayer
from collective.fingerpointing.testing import INTEGRATION_TESTING
from plone.browserlayer.utils import registered_layers

import unittest


class InstallTestCase(unittest.TestCase):

    """Ensure product is properly installed."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        self.assertIn(IBrowserLayer, registered_layers())

    def test_user_action(self):
        user_actions = self.portal['portal_actions'].user
        self.assertIn('audit-log', user_actions)

        permissions = user_actions['audit-log'].permissions
        expected = ('collective.fingerpointing: View Audit Log',)
        self.assertEqual(permissions, expected)
        url_expr = user_actions['audit-log'].url_expr
        self.assertIn('/@@fingerpointing-audit-log', url_expr)

    def test_setup_permission(self):
        permission = 'collective.fingerpointing: Setup'
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        expected = ['Manager', 'Site Administrator']
        self.assertListEqual(roles, expected)

    def test_show_log_permission(self):
        permission = 'collective.fingerpointing: View Audit Log'
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        expected = ['Manager', 'Site Administrator']
        self.assertListEqual(roles, expected)


class UninstallTestCase(unittest.TestCase):

    """Ensure product is properly uninstalled."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        self.assertNotIn(IBrowserLayer, registered_layers())

    def test_user_action_removed(self):
        user_actions = self.portal['portal_actions'].user
        self.assertNotIn('audit-log', user_actions)
