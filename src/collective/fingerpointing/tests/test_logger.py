"""Tests for the audit log destinations and formats."""
from collective.fingerpointing.config import fingerpointing_config
from collective.fingerpointing.config import read_config
from collective.fingerpointing.logger import AuditList
from collective.fingerpointing.logger import AuditObject
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.logger import syslog_address
from collective.fingerpointing.testing import INTEGRATION_TESTING
from plone import api
from testfixtures import LogCapture
from unittest import mock

import io
import json
import logging
import os
import socket
import tempfile
import unittest


class ConfigTestCase(unittest.TestCase):

    def test_product_config(self):
        config = read_config(
            {'collective.fingerpointing': {'audit-log': '/var/log/audit.log'}},
            {},
        )
        self.assertEqual(config, {'audit-log': '/var/log/audit.log'})

    def test_no_product_config(self):
        self.assertEqual(read_config({}, {}), {})

    def test_environment_overrides_product_config(self):
        config = read_config(
            {'collective.fingerpointing': {
                'audit-log': '/var/log/audit.log',
                'audit-log-format': 'text',
            }},
            {
                'FINGERPOINTING_AUDIT_LOG_HANDLER': 'stream',
                'FINGERPOINTING_AUDIT_LOG_FORMAT': 'json',
                'FINGERPOINTING_AUDIT_SYSLOG_ADDRESS': '',  # empty is ignored
                'OTHER': 'ignored',
            },
        )
        self.assertEqual(config, {
            'audit-log': '/var/log/audit.log',
            'audit-log-handler': 'stream',
            'audit-log-format': 'json',
        })

    def test_syslog_address(self):
        self.assertEqual(syslog_address('/dev/log'), '/dev/log')
        self.assertEqual(syslog_address('syslog'), ('syslog', 514))
        self.assertEqual(syslog_address('syslog:1514'), ('syslog', 1514))
        self.assertEqual(syslog_address('[::1]:1514'), ('::1', 1514))
        self.assertEqual(syslog_address('::1'), ('::1', 514))


class LoggerTestCase(unittest.TestCase):
    """Configure log_info with other settings, and restore the settings
    of the test fixture afterwards.
    """

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.temp_dir = tempfile.mkdtemp()
        self.logfile = os.path.join(self.temp_dir, 'audit.log')

    def tearDown(self):
        log_info.configure(fingerpointing_config)
        for name in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, name))
        os.rmdir(self.temp_dir)

    def configure(self, **settings):
        config = {k.replace('_', '-'): v for k, v in settings.items()}
        log_info.configure(config)

    def audit_login(self):
        log_info.audit('admin', '10.0.0.1', 'login failed', [('login', 'bob')])

    def read_logfile(self):
        with open(self.logfile, encoding='utf-8') as f:
            return f.read().splitlines()

    def test_text_format_is_default(self):
        self.configure(audit_log=self.logfile)
        self.audit_login()
        lines = self.read_logfile()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].endswith(
            ' - INFO - user=admin ip=10.0.0.1 action=login failed login=bob'))

    def test_text_format_escapes_newlines(self):
        self.configure(audit_log=self.logfile)
        log_info.audit('-', '10.0.0.1', 'login failed', [
            ('login', 'bob\n2024-01-01 - INFO - user=admin action=login'),
        ])
        lines = self.read_logfile()
        self.assertEqual(len(lines), 1)
        self.assertIn('login=bob\\n2024-01-01', lines[0])

    def test_json_format(self):
        self.configure(audit_log=self.logfile, audit_log_format='json')
        self.request['ACTUAL_URL'] = 'http://nohost/plone/@login'
        self.request['REQUEST_METHOD'] = 'POST'
        log_info.audit(
            'admin', '10.0.0.1', 'login failed', [('login', 'bob')],
            level=logging.WARNING)
        lines = self.read_logfile()
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        timestamp = entry.pop('timestamp')
        self.assertRegex(
            timestamp, r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$')
        self.assertEqual(entry, {
            'level': 'WARNING',
            'logger': 'collective.fingerpointing',
            'action': 'login failed',
            'user': 'admin',
            'ip': '10.0.0.1',
            'method': 'POST',
            'url': 'http://nohost/plone/@login',
            'details': {'login': 'bob'},
        })

    def test_json_format_objects_and_lists(self):
        self.configure(audit_log=self.logfile, audit_log_format='json')
        with api.env.adopt_roles(['Manager']):
            folder = api.content.create(self.portal, 'Folder', 'folder')
        log_info.audit('admin', '10.0.0.1', 'local roles change', [
            ('object', AuditObject(folder)),
            ('roles', AuditList(['Editor', 'Reader'])),
        ])
        entry = json.loads(self.read_logfile()[-1])
        self.assertEqual(entry['details'], {
            'object': {
                'path': '/plone/folder',
                'uid': folder.UID(),
                'type': 'Folder',
            },
            'roles': ['Editor', 'Reader'],
        })

    def test_json_format_plain_message(self):
        self.configure(audit_log=self.logfile, audit_log_format='json')
        log_info('something happened')
        entry = json.loads(self.read_logfile()[0])
        self.assertEqual(entry['message'], 'something happened')
        self.assertNotIn('action', entry)

    def test_unknown_format_falls_back_to_text(self):
        with LogCapture('fingerpointing common') as log:
            self.configure(audit_log=self.logfile, audit_log_format='xml')
        self.assertIn("Unknown audit-log-format 'xml'", str(log))
        self.audit_login()
        self.assertIn('action=login failed', self.read_logfile()[0])

    def test_no_handler(self):
        with LogCapture('fingerpointing common') as log:
            self.configure()
        self.assertIn('No audit log file specified', str(log))
        self.assertFalse(log_info.has_log_file)
        self.assertIsNone(log_info.handler)
        self.assertTrue(log_info.logger.propagate)

    def test_unknown_handler(self):
        with LogCapture('fingerpointing common') as log:
            self.configure(audit_log=self.logfile, audit_log_handler='kafka')
        self.assertIn("Unknown audit-log-handler 'kafka'", str(log))
        self.assertIsNone(log_info.handler)

    def test_file_handler_without_file_name(self):
        with LogCapture('fingerpointing common') as log:
            self.configure(audit_log_handler='file')
        self.assertIn('no audit-log file name is specified', str(log))
        self.assertIsNone(log_info.handler)

    def test_stream_handler(self):
        stdout = io.StringIO()
        with mock.patch('sys.stdout', stdout):
            self.configure(audit_log_handler='stream', audit_log_format='json')
        self.assertFalse(log_info.has_log_file)
        # the event log usually writes to the same stream
        self.assertFalse(log_info.logger.propagate)
        self.audit_login()
        entry = json.loads(stdout.getvalue())
        self.assertEqual(entry['action'], 'login failed')
        self.assertEqual(entry['details'], {'login': 'bob'})

    def test_reconfigure_removes_handler(self):
        stdout = io.StringIO()
        with mock.patch('sys.stdout', stdout):
            self.configure(audit_log_handler='stream')
        self.configure(audit_log=self.logfile)
        self.assertTrue(log_info.logger.propagate)
        self.audit_login()
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(len(self.read_logfile()), 1)

    def test_syslog_handler_udp(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(server.close)
        server.bind(('127.0.0.1', 0))
        server.settimeout(5)
        port = server.getsockname()[1]
        self.configure(
            audit_log_handler='syslog',
            audit_syslog_address=f'127.0.0.1:{port}',
            audit_syslog_facility='auth',
        )
        self.assertFalse(log_info.has_log_file)
        self.audit_login()
        message = server.recv(4096).decode('utf-8')
        # facility auth (4) * 8 + severity info (6) = 38
        self.assertEqual(
            message,
            '<38>collective.fingerpointing: '
            'user=admin ip=10.0.0.1 action=login failed login=bob\x00',
        )

    def test_syslog_handler_tcp_json(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(server.close)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        server.settimeout(5)
        port = server.getsockname()[1]
        self.configure(
            audit_log_handler='syslog',
            audit_log_format='json',
            audit_syslog_address=f'127.0.0.1:{port}',
            audit_syslog_socktype='tcp',
        )
        connection, _ = server.accept()
        self.addCleanup(connection.close)
        connection.settimeout(5)
        self.audit_login()
        message = b''
        while not message.endswith(b'\n'):
            message += connection.recv(4096)
        message = message.decode('utf-8')
        # facility user (1) * 8 + severity info (6) = 14
        prefix = '<14>collective.fingerpointing: '
        self.assertTrue(message.startswith(prefix))
        # one message per line: no NUL byte, newline at the end
        self.assertNotIn('\x00', message)
        entry = json.loads(message[len(prefix):])
        self.assertEqual(entry['action'], 'login failed')

    def test_syslog_handler_unreachable(self):
        # find a port nobody listens on
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        port = server.getsockname()[1]
        server.close()
        with LogCapture('fingerpointing common') as log:
            self.configure(
                audit_log_handler='syslog',
                audit_syslog_address=f'127.0.0.1:{port}',
                audit_syslog_socktype='tcp',
            )
        self.assertIn('Cannot log audit information to syslog', str(log))
        self.assertIsNone(log_info.handler)
        # audit events still reach the event log
        with LogCapture('collective.fingerpointing') as log:
            self.audit_login()
        self.assertIn('action=login failed', str(log))
