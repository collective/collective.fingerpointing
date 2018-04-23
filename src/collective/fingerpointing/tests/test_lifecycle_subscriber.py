# -*- coding: utf-8 -*-
"""Tests for lifecycle subscriber.

Events are slightly different among Archetypes and Dexterity.
Also, Dexterity content types have different names.
"""
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import IS_PLONE_5
from collective.fingerpointing.testing import QIBBB
from logging import INFO
from plone import api
from testfixtures import LogCapture

import unittest


class LifeCycleSubscribersTestCase(unittest.TestCase, QIBBB):
    """Tests content type life cycle subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')

    def test_file_lifecicle(self):
        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create object=<File at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<Folder at /plone/folder>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove object=<File at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<Folder at /plone/folder>'),  # noqa: E501
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create object=<ATFile at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATFolder at /plone/folder>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATFile at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove object=<ATFile at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATFolder at /plone/folder>'),  # noqa: E501
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            obj = api.content.create(self.folder, 'File', 'foo')
            obj.reindexObject()
            api.content.delete(obj)
            log.check(*expected)

    def test_folder_lifecicle(self):
        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create object=<Folder at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<Folder at /plone/folder>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove object=<Folder at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<Folder at /plone/folder>'),  # noqa: E501
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create object=<ATFolder at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATFolder at /plone/folder>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATFolder at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove object=<ATFolder at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATFolder at /plone/folder>'),  # noqa: E501
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            obj = api.content.create(self.folder, 'Folder', 'foo')
            obj.reindexObject()
            api.content.delete(obj)
            log.check(*expected)

    def test_image_lifecicle(self):
        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create object=<Image at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<Folder at /plone/folder>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove object=<Image at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<Folder at /plone/folder>'),  # noqa: E501
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create object=<ATImage at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATFolder at /plone/folder>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATImage at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove object=<ATImage at /plone/folder/foo>'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=modify object=<ATFolder at /plone/folder>'),  # noqa: E501
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            obj = api.content.create(self.folder, 'Image', 'foo')
            obj.reindexObject()
            api.content.delete(obj)
            log.check(*expected)

    def test_susbcriber_ignored_when_package_not_installed(self):
        # content type life cycle events should not raise errors
        # if package is not installed
        self.uninstall()  # BBB: QI compatibility

        obj = api.content.create(self.folder, 'Folder', 'foo')
        obj.reindexObject()
        api.content.delete(obj)
