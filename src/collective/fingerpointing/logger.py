# -*- coding: utf-8 -*-
from App.config import getConfiguration
from collective.fingerpointing.config import AUDITLOG
from collective.fingerpointing.config import PROJECTNAME

import logging
import os.path
import time
import zc.lockfile


FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# by default, the audit log will use the same location used for the event log
eventlog = getattr(getConfiguration(), 'eventlog', None)

if eventlog is None:
    # we are running tests
    logfile = os.path.join('.', AUDITLOG)
else:
    try:
        logpath = eventlog.handler_factories[0].instance.baseFilename
        logfolder = os.path.split(logpath)[0]
        logfile = os.path.join(logfolder, AUDITLOG)
    except AttributeError:
        # we are in the debug console
        logfile = os.path.join('.', AUDITLOG)

logger = logging.getLogger(PROJECTNAME)
logger.setLevel(logging.INFO)
logger.info('Start logging audit information to ' + AUDITLOG)

# support automatic rotation of audit log files at timed intervals
# we can later implement a way to make this configurable
handler = logging.handlers.TimedRotatingFileHandler(
    logfile, when='midnight', backupCount=30)

formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_info(*args, **kwargs):
    """Log information to a file handling access from multiple instances.
    This code was taken from ZEO/ClientStorage.py.
    """
    # try to lock the logfile then write to the logfile
    lockfilename = logfile + '.lock'
    n = 0

    while 1:
        try:
            lock = zc.lockfile.LockFile(lockfilename)
            logger.info(*args, **kwargs)
            lock.close()
        except zc.lockfile.LockError:
            time.sleep(0.01)
            n += 1
            if n > 60000:
                raise
        else:
            break

    return
