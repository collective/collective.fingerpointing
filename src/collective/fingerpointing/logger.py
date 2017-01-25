# -*- coding: utf-8 -*-
from collective.fingerpointing.config import fingerpointing_config
from collective.fingerpointing.config import LOG_FORMAT
from collective.fingerpointing.config import PROJECTNAME

import logging
import time
import zc.lockfile


logger = logging.getLogger(PROJECTNAME)
logger.setLevel(logging.INFO)

logfile = fingerpointing_config.get('audit-log', None)
if logfile is None:
    logger.warn('No audit log file specified; audit log view will be disabled')
else:
    # if either of maxBytes or backupCount is zero, rollover never occurs
    maxBytes = int(fingerpointing_config.get('audit-log-max-size', 0))
    backupCount = int(fingerpointing_config.get('audit-log-old-files', 1))
    handler = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=maxBytes, backupCount=backupCount)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('Logging audit information to ' + logfile)


def log_info(*args, **kwargs):
    """Log information to a file handling access from multiple instances.
    This code was taken from ZEO/ClientStorage.py.
    """
    # if no logfile was specified just log the event normally
    if logfile is None:
        logger.info(*args, **kwargs)
        return

    # otherwise, try to lock the logfile then writing to it
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
