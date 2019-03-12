# -*- coding: utf-8 -*-
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import QIBBB
from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


class ControlPanelTestCase(unittest.TestCase, QIBBB):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.controlpanel = self.portal['portal_controlpanel']

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@fingerpointing-settings')

    def test_controlpanel_installed(self):
        actions = [
            a.getAction(self)['id'] for a in self.controlpanel.listActions()]
        self.assertIn('fingerpointing', actions)

    def test_controlpanel_removed_on_uninstall(self):
        self.uninstall()  # BBB: QI compatibility

        actions = [
            a.getAction(self)['id'] for a in self.controlpanel.listActions()]
        self.assertNotIn('fingerpointing', actions)


class RegistryTestCase(unittest.TestCase, QIBBB):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IFingerPointingSettings)

    def test_audit_pas_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'audit_pas'))
        self.assertEqual(self.settings.audit_pas, True)

    def test_audit_lifecycle_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'audit_lifecycle'))
        self.assertEqual(self.settings.audit_lifecycle, True)

    def test_audit_workflow_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'audit_workflow'))
        self.assertEqual(self.settings.audit_workflow, True)

    def test_audit_profile_imports_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'audit_profile_imports'))
        self.assertEqual(self.settings.audit_profile_imports, True)

    def test_audit_registry_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'audit_registry'))
        self.assertEqual(self.settings.audit_registry, True)

    def test_audit_iterate_record_in_registry(self):
        self.assertTrue(hasattr(self.settings, 'audit_iterate'))
        self.assertEqual(self.settings.audit_iterate, True)

    def test_records_removed_on_uninstall(self):
        self.uninstall()  # BBB: QI compatibility

        records = [
            IFingerPointingSettings.__identifier__ + '.audit_pas',
            IFingerPointingSettings.__identifier__ + '.audit_lifecycle',
            IFingerPointingSettings.__identifier__ + '.audit_workflow',
            IFingerPointingSettings.__identifier__ + '.audit_profile_imports',
            IFingerPointingSettings.__identifier__ + '.audit_registry',
            IFingerPointingSettings.__identifier__ + '.audit_iterate',
        ]
        for r in records:
            self.assertNotIn(r, self.registry)
