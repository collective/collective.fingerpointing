# -*- coding: utf-8 -*-
from collective.fingerpointing.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import logout

import unittest


def _fresh_audit_log(*lines):
    """Empty the audit log files, then write these lines."""
    from collective.fingerpointing.config import fingerpointing_config
    from collective.fingerpointing.logger import log_info
    from collective.fingerpointing.utils import audit_log_files

    import os

    for filename in audit_log_files():
        os.remove(filename)
    log_info.configure(fingerpointing_config)
    for line in lines:
        log_info(line)


class LogViewTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.view = api.content.get_view(
            'fingerpointing-audit-log', self.portal, self.request)

    def test_audit_log_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@fingerpointing-audit-log')

    def test_available(self):
        self.assertTrue(self.view.available)

    def test_page_and_size_defaults(self):
        self.assertEqual(self.view.page, 1)
        self.assertEqual(self.view.size, 100)
        self.assertEqual(self.view.query, '')

    def test_page_and_size_from_request(self):
        self.request.form.update({'page': '3', 'size': '50', 'query': ' foo '})
        self.assertEqual(self.view.page, 3)
        self.assertEqual(self.view.size, 50)
        self.assertEqual(self.view.query, 'foo')

    def test_invalid_page_and_size(self):
        self.request.form.update({'page': 'x', 'size': 'y'})
        self.assertEqual(self.view.page, 1)
        self.assertEqual(self.view.size, 100)

    def test_build_audit_log_newest_first(self):
        _fresh_audit_log('line one', 'line two', 'line three')
        self.view.build_audit_log()
        lines = self.view.audit_log.split('\n')
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].endswith(' - INFO - line three'))
        self.assertTrue(lines[1].endswith(' - INFO - line two'))
        self.assertTrue(lines[2].endswith(' - INFO - line one'))
        self.assertFalse(self.view.has_next)
        self.assertFalse(self.view.has_prev)

    def test_build_audit_log_filtered(self):
        _fresh_audit_log('apple', 'banana', 'apple pie')
        self.request.form['query'] = 'apple'
        self.view.build_audit_log()
        lines = self.view.audit_log.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].endswith('apple pie'))
        self.assertTrue(lines[1].endswith('apple'))

    def test_build_audit_log_batched(self):
        _fresh_audit_log('1', '2', '3', '4', '5')
        self.request.form.update({'size': '2', 'page': '2'})
        self.view.build_audit_log()
        lines = [line[-1] for line in self.view.audit_log.split('\n')]
        self.assertEqual(lines, ['3', '2'])
        self.assertTrue(self.view.has_next)
        self.assertTrue(self.view.has_prev)

    def test_pagination_url(self):
        self.request.form.update({'size': '2', 'page': '2', 'query': 'foo'})
        base = self.portal.absolute_url() + '/@@fingerpointing-audit-log?'

        def params(url):
            self.assertTrue(url.startswith(base))
            return sorted(url[len(base):].split('&'))

        self.assertEqual(
            params(self.view.pagination_url('first')),
            ['page=1', 'query=foo', 'size=2'])
        self.assertEqual(
            params(self.view.pagination_url('prev')),
            ['page=1', 'query=foo', 'size=2'])
        self.assertEqual(
            params(self.view.pagination_url('next')),
            ['page=3', 'query=foo', 'size=2'])
        self.assertEqual(
            params(self.view.pagination_url('size', 50)),
            ['query=foo', 'size=50'])

    def test_render(self):
        _fresh_audit_log('rendered line')
        html = self.view()
        self.assertIn('Audit Log', html)
        self.assertIn('rendered line', html)
        self.assertIn('name="query"', html)
        self.assertNotIn('audit log view is disabled', html)

    def test_render_without_audit_log_file(self):
        from collective.fingerpointing.logger import log_info
        logfile = log_info.logfile
        log_info.logfile = None
        try:
            self.assertFalse(self.view.available)
            html = self.view()
        finally:
            log_info.logfile = logfile
        self.assertIn('No audit log file specified; audit log view is disabled.', html)
        self.assertNotIn('name="query"', html)


class LogInfoTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def test_without_log_file(self):
        from collective.fingerpointing.logger import LogInfo
        from logging import INFO
        from testfixtures import LogCapture
        log_info = LogInfo({})
        self.assertFalse(log_info.has_log_file)
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            log_info('not written to a file')
            log.check(('collective.fingerpointing', 'INFO', 'not written to a file'))
