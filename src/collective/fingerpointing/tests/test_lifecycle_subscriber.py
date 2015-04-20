# -*- coding: utf-8 -*-
from collective.fingerpointing.testing import INTEGRATION_TESTING
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

    def test_object_created(self):
        with LogCapture(level=INFO) as log:
            api.content.create(self.folder, 'Folder', 'foo')
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=object created object=<ATFolder at foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=object modified object=<ATFolder at folder>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=object modified object=<ATFolder at foo>'),
            )

    def test_object_removed(self):
        api.content.create(self.folder, 'Folder', 'foo')
        with LogCapture(level=INFO) as log:
            api.content.delete(self.folder['foo'])
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=object removed object=<ATFolder at foo>'),
                ('collective.fingerpointing', 'INFO', 'user=test ip=127.0.0.1 action=object modified object=<ATFolder at folder>'),
            )
