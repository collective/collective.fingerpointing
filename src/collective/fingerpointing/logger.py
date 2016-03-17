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

# on tests, eventlog is not set; we need to handle that
if eventlog is not None:
    logpath = eventlog.handler_factories[0].instance.baseFilename
    logfolder = os.path.split(logpath)[0]
    logfile = os.path.join(logfolder, AUDITLOG)
else:
    logfile = AUDITLOG

logger = logging.getLogger(PROJECTNAME)
logger.setLevel(logging.INFO)
logger.info('Start logging audit information to ' + AUDITLOG)

handler = logging.FileHandler(logfile)
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
