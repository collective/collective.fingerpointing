# -*- coding: utf-8 -*-
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.testing import INTEGRATION_TESTING
from logging import INFO
from plone import api
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from testfixtures import LogCapture
from zope.component import getUtility

import unittest


class RegistrySubscribersTestCase(unittest.TestCase):

    """Tests for plone.app.registry subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_record_modified(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            record = IDiscussionSettings.__identifier__ + '.globally_enabled'
            api.portal.set_registry_record(record, False)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<Record plone.app.discussion.interfaces.IDiscussionSettings.globally_enabled> value=False'),
            )

    def test_new_record_modified(self):
        registry = getUtility(IRegistry)
        registry.records['collective.fingerpointing.new_field'] = Record(
            field.TextLine(title=u'New field'))
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            api.portal.set_registry_record('collective.fingerpointing.new_field', u'Descrição')
            log.check(
                ('collective.fingerpointing', 'INFO', u'user=test ip=127.0.0.1 action=modify object=<Record collective.fingerpointing.new_field> value=Descrição'),
            )

    def test_susbcriber_ignored_when_package_not_installed(self):
        # registry events should not raise errors
        # if package is not installed
        qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])

        record = IDiscussionSettings.__identifier__ + '.globally_enabled'
        api.portal.set_registry_record(record, False)
