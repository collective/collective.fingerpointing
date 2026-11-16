# -*- coding: utf-8 -*-
"""Each audit setting of the control panel turns its subscriber off."""
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.testing import INTEGRATION_TESTING
from logging import INFO
from plone import api
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.PlonePAS.events import UserLoggedInEvent
from testfixtures import LogCapture
from zope.event import notify

import unittest


def _disable(*names):
    for name in names:
        api.portal.set_registry_record(
            IFingerPointingSettings.__identifier__ + "." + name, False
        )


class SettingsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        # registry changes made by the tests themselves are not audited
        _disable("audit_registry")

    def test_audit_pas_disabled(self):
        _disable("audit_pas")
        with LogCapture("collective.fingerpointing", level=INFO) as log:
            notify(UserLoggedInEvent(api.user.get_current()))
            log.check()

    def test_audit_lifecycle_disabled(self):
        _disable("audit_lifecycle")
        with LogCapture("collective.fingerpointing", level=INFO) as log:
            obj = api.content.create(self.portal, "Folder", "foo")
            api.content.delete(obj)
            log.check()

    def test_audit_workflow_disabled(self):
        _disable("audit_lifecycle", "audit_workflow")
        obj = api.content.create(self.portal, "News Item", "foo")
        with LogCapture("collective.fingerpointing", level=INFO) as log:
            api.content.transition(obj=obj, transition="publish")
            log.check()

    def test_audit_registry_disabled(self):
        with LogCapture("collective.fingerpointing", level=INFO) as log:
            _disable("audit_pas")
            log.check()

    def test_audit_iterate_disabled(self):
        _disable("audit_lifecycle", "audit_iterate")
        doc = api.content.create(self.portal, "Document", "doc")
        with LogCapture("collective.fingerpointing", level=INFO) as log:
            wc = ICheckinCheckoutPolicy(doc).checkout(self.portal)
            ICheckinCheckoutPolicy(wc).cancelCheckout()
            log.check()

    def test_audit_profile_imports_disabled(self):
        _disable("audit_profile_imports")
        setup_tool = api.portal.get_tool("portal_setup")
        with LogCapture("collective.fingerpointing", level=INFO) as log:
            setup_tool.runAllImportStepsFromProfile(
                "profile-collective.fingerpointing:default"
            )
            log.check()

    def test_audit_profile_imports_enabled(self):
        # control of the test above: the same import is audited when enabled
        setup_tool = api.portal.get_tool("portal_setup")
        with LogCapture("collective.fingerpointing", level=INFO) as log:
            setup_tool.runAllImportStepsFromProfile(
                "profile-collective.fingerpointing:default"
            )
        self.assertIn(
            "action=profile imported id=collective.fingerpointing:default",
            [r.getMessage() for r in log.records][-1],
        )
