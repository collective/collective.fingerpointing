# -*- coding: utf-8 -*-
from collective.fingerpointing.testing import INTEGRATION_TESTING

import unittest


class UtilsTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']

    def test_get_request_information(self):
        from collective.fingerpointing import utils
        self.assertEqual(
            utils.get_request_information(), ('test_user_1_', 'None'))

    def test_get_request_information_anonymous(self):
        from plone.app.testing import logout
        logout()
        from collective.fingerpointing import utils
        self.assertEqual(utils.get_request_information(), ('-', 'None'))

    def test_get_request_information_cloudflare(self):
        self.request.environ['HTTP_CF_CONNECTING_IP'] = '192.168.1.1'
        from collective.fingerpointing import utils
        self.assertEqual(
            utils.get_request_information(), ('test_user_1_', '192.168.1.1'))

    def test_audit_log_files(self):
        from collective.fingerpointing import utils
        audit_log_files = utils.audit_log_files()
        # we have at least one log file to process
        self.assertGreaterEqual(len(audit_log_files), 1)
        # the first file is the current audit log
        self.assertEqual('/audit.log', audit_log_files[0][-10:])


class UtilsOneLargeLogFileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        # fresh audit log
        from collective.fingerpointing.config import fingerpointing_config
        from collective.fingerpointing.logger import log_info
        from collective.fingerpointing.utils import audit_log_files
        import os
        for filename in audit_log_files():
            os.remove(filename)
        log_info.configure(fingerpointing_config)

    def test_audit_log_lines_of(self):
        from collective.fingerpointing.logger import log_info
        # prepare some loglines
        log_info('1')
        log_info('2')
        log_info('3')
        from collective.fingerpointing import utils
        audit_log_files = utils.audit_log_files()
        self.assertEqual(len(audit_log_files), 1)
        lines_gen = utils.audit_log_lines_of(audit_log_files[0])
        self.assertEqual(next(lines_gen)[-1], '3')
        self.assertEqual(next(lines_gen)[-1], '2')
        self.assertEqual(next(lines_gen)[-1], '1')


class UtilsMultipleLogFilesTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        # create more than one logfile
        from collective.fingerpointing.config import fingerpointing_config
        from collective.fingerpointing.logger import log_info
        from collective.fingerpointing.utils import audit_log_files
        import os
        for filename in audit_log_files():
            os.remove(filename)
        fingerpointing_config['audit-log-max-size'] = 80
        fingerpointing_config['audit-log-old-files'] = 10
        log_info.configure(fingerpointing_config)

    def tearDown(self):
        from collective.fingerpointing.config import fingerpointing_config
        from collective.fingerpointing.logger import log_info
        del fingerpointing_config['audit-log-max-size']
        log_info.configure(fingerpointing_config)

    def test_all_audit_log_lines(self):
        from collective.fingerpointing.logger import log_info
        # prepare some loglines to create 2 files
        log_info('1')
        log_info('2')
        log_info('3')
        log_info('4')
        # check for min 2 files
        from collective.fingerpointing import utils
        audit_log_files = utils.audit_log_files()
        self.assertGreaterEqual(len(audit_log_files), 2)
        # check if we get all entries reversed
        lines_gen = utils.all_audit_log_lines()
        self.assertEqual(next(lines_gen)[-1], '4')
        self.assertEqual(next(lines_gen)[-1], '3')
        self.assertEqual(next(lines_gen)[-1], '2')
        self.assertEqual(next(lines_gen)[-1], '1')
