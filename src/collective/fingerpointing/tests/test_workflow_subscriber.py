# -*- coding: utf-8 -*-
"""Tests for workflow subscriber."""
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.testing import INTEGRATION_TESTING
from logging import INFO
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from testfixtures import LogCapture

import unittest


class WorkflowSubscribersTestCase(unittest.TestCase):

    """Tests content type life cycle subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # disable lifecycle audit
        record = IFingerPointingSettings.__identifier__ + '.audit_lifecycle'
        api.portal.set_registry_record(record, False)

    def test_workflow_transitions(self):
        expected = (
            ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<NewsItem at foo> transition=submit'),
            ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<NewsItem at foo> transition=publish'),
            ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<NewsItem at foo> transition=retract'),
        )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            obj = api.content.create(self.portal, 'News Item', 'foo')
            api.content.transition(obj=obj, transition='submit')
            api.content.transition(obj=obj, transition='publish')
            api.content.transition(obj=obj, transition='retract')
            log.check(*expected)

    def test_susbcriber_ignored_when_package_not_installed(self):
        # events should not raise errors if package is not installed
        qi = self.portal['portal_quickinstaller']
        qi.uninstallProducts(products=[PROJECTNAME])

        obj = api.content.create(self.portal, 'News Item', 'foo')
        api.content.transition(obj=obj, transition='submit')
        api.content.transition(obj=obj, transition='publish')
        api.content.transition(obj=obj, transition='retract')
