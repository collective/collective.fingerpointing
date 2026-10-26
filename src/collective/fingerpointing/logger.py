from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.config import fingerpointing_config
from collective.fingerpointing.config import LOG_FORMAT
from collective.fingerpointing.config import PROJECTNAME
from datetime import datetime
from datetime import timezone
from zope.globalrequest import getRequest

import json
import logging
import logging.handlers
import socket
import sys
import time
import zc.lockfile


commonlogger = logging.getLogger('fingerpointing common')

HANDLERS = ('file', 'syslog', 'stream')
FORMATS = ('text', 'json')
SYSLOG_FORMAT = '%(message)s'


class AuditObject:
    """A content object in the details of an audit event.

    The text format shows ``text(obj)``, like 1.x did; the JSON format shows
    the path, UID and portal type of the object.
    """

    def __init__(self, obj, text=repr):
        self.obj = obj
        self.text = text

    def __str__(self):
        return self.text(self.obj)

    def as_json(self):
        obj = self.obj
        if not hasattr(obj, 'getPhysicalPath'):
            return str(self)
        data = {'path': '/'.join(obj.getPhysicalPath())}
        uid = getattr(obj, 'UID', None)
        if callable(uid):
            data['uid'] = uid()
        portal_type = getattr(obj, 'portal_type', None)
        if portal_type:
            data['type'] = portal_type
        return data


class AuditList(tuple):
    """A list of values (e.g. roles), comma separated in the text format."""

    def __str__(self):
        return ','.join(str(v) for v in self)


def text_value(value):
    """Render a detail value for the text format, on a single line."""
    # user input (e.g. a login name) must not be able to forge log lines
    return str(value).replace('\r', '\\r').replace('\n', '\\n')


def json_value(value):
    """Render a detail value for the JSON format."""
    if isinstance(value, AuditObject):
        return value.as_json()
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple, set, frozenset)):
        return [json_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    return str(value)


class JSONFormatter(logging.Formatter):
    """Format each record as a single line of JSON."""

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created, timezone.utc)
        entry = {
            'timestamp': timestamp.isoformat(timespec='milliseconds').replace(
                '+00:00', 'Z'),
            'level': record.levelname,
            'logger': record.name,
        }
        audit = getattr(record, 'audit', None)
        if audit is None:  # plain log_info('message') calls
            entry['message'] = record.getMessage()
        else:
            entry.update(audit)
        return json.dumps(entry, ensure_ascii=False, default=str)


class SysLogHandler(logging.handlers.SysLogHandler):
    """SysLogHandler that frames messages over TCP with a newline,
    which syslog servers accept (RFC 6587 non-transparent framing).
    """

    def format(self, record):
        message = super().format(record)
        if self.socktype == socket.SOCK_STREAM:
            message += '\n'
        return message


def syslog_address(value):
    """Parse 'host:port', 'host', '[ipv6]:port' or a unix socket path
    like '/dev/log'.
    """
    if value.startswith('/'):
        return value
    host, sep, port = value.rpartition(':')
    if not sep or host.count(':') and not host.endswith(']'):
        # no port, or a bare IPv6 address
        return (value.strip('[]'), logging.handlers.SYSLOG_UDP_PORT)
    return (host.strip('[]'), int(port))


class LogInfo:

    def __init__(self, config, logformat=LOG_FORMAT):
        self.logger = logging.getLogger(PROJECTNAME)
        self.logfile = None
        self.handler = None
        self.configure(config, logformat)

    @property
    def has_log_file(self):
        return bool(self.logfile)

    def configure(self, config, logformat=LOG_FORMAT):
        # first remove old handler if set:
        if self.handler is not None:
            self.logger.removeHandler(self.handler)
            self.handler.close()
            self.handler = None
        self.logfile = None
        self.logger.propagate = True

        log_format = config.get('audit-log-format') or 'text'
        if log_format not in FORMATS:
            commonlogger.warning(
                'Unknown audit-log-format %r; using text', log_format)
            log_format = 'text'

        handler_type = config.get('audit-log-handler')
        if not handler_type and config.get('audit-log'):
            handler_type = 'file'
        if not handler_type:
            commonlogger.warning(
                'No audit log file specified; audit log view will be disabled')
            return None
        if handler_type not in HANDLERS:
            commonlogger.warning(
                'Unknown audit-log-handler %r; audit events are only '
                'logged to the event log', handler_type)
            return None

        if handler_type == 'file':
            handler = self._file_handler(config)
            formatter = logging.Formatter(logformat)
        elif handler_type == 'syslog':
            handler = self._syslog_handler(config)
            formatter = logging.Formatter(SYSLOG_FORMAT)
        else:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(logformat)
            # the event log usually goes to the same stream: log only once
            self.logger.propagate = False
        if handler is None:
            return None

        if log_format == 'json':
            formatter = JSONFormatter()
        handler.setFormatter(formatter)
        self.handler = handler
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        return None

    def _file_handler(self, config):
        logfile = config.get('audit-log')
        if not logfile:
            commonlogger.warning(
                'audit-log-handler is file, but no audit-log file name is '
                'specified; audit events are only logged to the event log')
            return None
        # if either of maxBytes or backupCount is zero, rollover never occurs
        maxBytes = int(config.get('audit-log-max-size', 0))
        backupCount = int(config.get('audit-log-old-files', 0))
        handler = logging.handlers.RotatingFileHandler(
            logfile,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding='utf-8',
            delay=True,  # defer file creation to first emit
        )
        self.logfile = logfile
        commonlogger.info('Logging audit information to ' + logfile)
        return handler

    def _syslog_handler(self, config):
        address = config.get('audit-syslog-address') or 'localhost'
        socktype = config.get('audit-syslog-socktype') or 'udp'
        facility = config.get('audit-syslog-facility') or 'user'
        if facility not in SysLogHandler.facility_names:
            commonlogger.warning(
                'Unknown audit-syslog-facility %r; using user', facility)
            facility = 'user'
        try:
            handler = SysLogHandler(
                address=syslog_address(address),
                facility=SysLogHandler.facility_names[facility],
                socktype=(
                    socket.SOCK_STREAM if socktype == 'tcp'
                    else socket.SOCK_DGRAM),
            )
        except (OSError, ValueError):
            # do not keep Zope from starting; but make some noise
            commonlogger.exception(
                'Cannot log audit information to syslog at %s; audit events '
                'are only logged to the event log', address)
            return None
        handler.ident = PROJECTNAME + ': '
        if socktype == 'tcp':
            # messages are framed with a newline, see SysLogHandler.format
            handler.append_nul = False
        commonlogger.info(
            'Logging audit information to syslog at %s (%s)', address, socktype)
        return handler

    def __call__(self, *args, **kwargs):
        """Log a message as is; kept for code that calls log_info directly.
        """
        self._log(logging.INFO, *args, **kwargs)

    def audit(self, user, ip, action, details=(), level=logging.INFO):
        """Log an audit event.

        ``details`` is a sequence of (name, value) pairs. The text format
        writes them as ``name=value`` after the action; the JSON format
        writes them as an object under ``details``.
        """
        details = list(details)
        extras = ' '.join(
            f'{name}={text_value(value)}'
            for name, value in details)
        message = AUDIT_MESSAGE.format(user, ip, action, extras)
        entry = {'action': action, 'user': user, 'ip': ip}
        request = getRequest()
        if request is not None:
            entry['method'] = request.get('REQUEST_METHOD')
            entry['url'] = request.get('ACTUAL_URL')
        entry['details'] = {name: json_value(value) for name, value in details}
        self._log(level, message, extra={'audit': entry})

    def _log(self, level, *args, **kwargs):
        # if no logfile was specified just log the event normally
        if self.logfile is None:
            self.logger.log(level, *args, **kwargs)
            return

        # otherwise, try to lock the self.logfile then writing to it.
        # This code was taken from ZEO/ClientStorage.py.
        lockfilename = self.logfile + '.lock'
        n = 0

        while 1:
            try:
                # A content_template with hostname makes the implementation
                # container save, where each process in the different
                # containers is likely to have the same PID.
                # https://pypi.python.org/pypi/zc.lockfile#hostname-in-lock-file
                lock = zc.lockfile.LockFile(
                    lockfilename,
                    content_template='{pid};{hostname}',
                )
                try:
                    self.logger.log(level, *args, **kwargs)
                finally:
                    # even if logging fails: release the lock.
                    lock.close()
            except zc.lockfile.LockError:
                time.sleep(0.01)
                n += 1
                if n > 60000:
                    raise
            else:
                break


log_info = LogInfo(fingerpointing_config)
