# -*- coding: utf-8 -*-
"""Tests for workflow subscriber."""
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import IS_PLONE_5
from collective.fingerpointing.testing import QIBBB
from logging import INFO
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from testfixtures import LogCapture

import unittest


class WorkflowSubscribersTestCase(unittest.TestCase, QIBBB):
    """Tests content type life cycle subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # disable lifecycle audit
        record = IFingerPointingSettings.__identifier__ + '.audit_lifecycle'
        api.portal.set_registry_record(record, False)

    def test_workflow_transitions(self):

        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<NewsItem at /plone/foo> transition=submit'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<NewsItem at /plone/foo> transition=publish'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<NewsItem at /plone/foo> transition=retract'),  # noqa: E501
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<ATNewsItem at /plone/foo> transition=submit'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<ATNewsItem at /plone/foo> transition=publish'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', u'user=test_user_1_ ip=None action=workflow transition object=<ATNewsItem at /plone/foo> transition=retract'),  # noqa: E501
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            obj = api.content.create(self.portal, 'News Item', 'foo')
            api.content.transition(obj=obj, transition='submit')
            api.content.transition(obj=obj, transition='publish')
            api.content.transition(obj=obj, transition='retract')
            log.check(*expected)

    def test_susbcriber_ignored_when_package_not_installed(self):
        # events should not raise errors if package is not installed
        self.uninstall()  # BBB: QI compatibility

        obj = api.content.create(self.portal, 'News Item', 'foo')
        api.content.transition(obj=obj, transition='submit')
        api.content.transition(obj=obj, transition='publish')
        api.content.transition(obj=obj, transition='retract')
