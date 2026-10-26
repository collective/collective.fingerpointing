from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import UninstallMixin
from logging import INFO
from plone import api
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from testfixtures import LogCapture
from zope.component import getUtility

import unittest


class RegistrySubscribersTestCase(unittest.TestCase, UninstallMixin):
    """Tests for plone.app.registry subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_record_modified(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            api.portal.set_registry_record('plone.display_publication_date_in_byline', True)  # noqa: E501
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<Record plone.display_publication_date_in_byline> value=True'),  # noqa: E501
            )

    def test_new_record_modified(self):
        registry = getUtility(IRegistry)
        registry.records['collective.fingerpointing.new_field'] = Record(
            field.TextLine(title='New field'))
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            api.portal.set_registry_record('collective.fingerpointing.new_field', 'Descrição')  # noqa: E501
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<Record collective.fingerpointing.new_field> value=Descrição'),  # noqa: E501
            )

    def test_susbcriber_ignored_when_package_not_installed(self):
        # registry events should not raise errors
        # if package is not installed
        self.uninstall()

        api.portal.set_registry_record('plone.display_publication_date_in_byline', True)  # noqa: E501
