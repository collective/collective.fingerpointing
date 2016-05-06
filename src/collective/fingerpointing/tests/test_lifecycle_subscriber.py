# -*- coding: utf-8 -*-
"""Tests for lifecycle subscriber.

Events are slightly different among Archetypes and Dexterity.
Also, Dexterity content types have different names.
"""
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import IS_PLONE_5
from logging import INFO
from plone import api
from testfixtures import LogCapture

import unittest


class LifeCycleSubscribersTestCase(unittest.TestCase):

    """Tests content type life cycle subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        with api.env.adopt_roles(['Manager']):
            self.folder = api.content.create(self.portal, 'Folder', 'folder')

    def test_file_lifecicle(self):
        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=create object=<File at foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<Folder at /plone/folder>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=remove object=<File at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<Folder at /plone/folder>'),
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=create object=<ATFile at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATFolder at /plone/folder>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATFile at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=remove object=<ATFile at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATFolder at /plone/folder>'),
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            obj = api.content.create(self.folder, 'File', 'foo')
            obj.reindexObject()
            api.content.delete(obj)
            log.check(*expected)

    def test_folder_lifecicle(self):
        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=create object=<Folder at foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<Folder at /plone/folder>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=remove object=<Folder at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<Folder at /plone/folder>'),
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=create object=<ATFolder at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATFolder at /plone/folder>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATFolder at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=remove object=<ATFolder at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATFolder at /plone/folder>'),
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            obj = api.content.create(self.folder, 'Folder', 'foo')
            obj.reindexObject()
            api.content.delete(obj)
            log.check(*expected)

    def test_image_lifecicle(self):
        if IS_PLONE_5:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=create object=<Image at foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<Folder at /plone/folder>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=remove object=<Image at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<Folder at /plone/folder>'),
            )
        else:
            expected = (
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=create object=<ATImage at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATFolder at /plone/folder>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATImage at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=remove object=<ATImage at /plone/folder/foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=modify object=<ATFolder at /plone/folder>'),
            )

        with LogCapture('collective.fingerpointing', level=INFO) as log:
            obj = api.content.create(self.folder, 'Image', 'foo')
            obj.reindexObject()
            api.content.delete(obj)
            log.check(*expected)

    def test_susbcriber_ignored_when_package_not_installed(self):
        # content type life cycle events should not raise errors
        # if package is not installed
        qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])

        obj = api.content.create(self.folder, 'Folder', 'foo')
        obj.reindexObject()
        api.content.delete(obj)
