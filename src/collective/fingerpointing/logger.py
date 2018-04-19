# -*- coding: utf-8 -*-
from collective.fingerpointing.config import fingerpointing_config
from collective.fingerpointing.config import LOG_FORMAT
from collective.fingerpointing.config import PROJECTNAME

import logging
import time
import zc.lockfile


commonlogger = logging.getLogger('fingerpointing common')


class LogInfo(object):

    def __init__(self, config, logformat=LOG_FORMAT):
        self.logger = logging.getLogger(PROJECTNAME)
        self.logfile = None
        self.handler = None
        self.configure(config)

    @property
    def has_log_file(self):
        return bool(self.logfile)

    def configure(self, config, logformat=LOG_FORMAT):
        self.logfile = config.get('audit-log', None)
        if self.logfile is None:
            commonlogger.warn(
                'No audit log file specified; audit log view will be disabled')
            return None

        self.logger.setLevel(logging.INFO)
        # first remove old handler if set:
        if self.handler is not None:
            self.logger.removeHandler(self.handler)
        # if backupCount is zero, rollover never occurs
        backupCount = int(config.get('audit-log-old-files', 0))
        self.handler = logging.handlers.TimedRotatingFileHandler(
            self.logfile,
            when='midnight',  # roll over at midnight
            backupCount=backupCount,
            delay=True,  # defer file creation to first emit
        )
        formatter = logging.Formatter(logformat)
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        commonlogger.info('Logging audit information to ' + self.logfile)
        if backupCount:
            msg = 'At most {0} backup files will be kept'.format(backupCount)
            commonlogger.info(msg)
        else:
            commonlogger.warn('No backup files will be kept')

    def __call__(self, *args, **kwargs):
        """Log information to a file handling access from multiple instances.
        This code was taken from ZEO/ClientStorage.py.
        """
        # if no logfile was specified just log the event normally
        if self.logfile is None:
            self.logger.info(*args, **kwargs)
            return

        # otherwise, try to lock the self.logfile then writing to it
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
                    self.logger.info(*args, **kwargs)
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
