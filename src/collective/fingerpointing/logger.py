# -*- coding: utf-8 -*-
from App.config import getConfiguration
from collective.fingerpointing.config import AUDITLOG
from collective.fingerpointing.config import PROJECTNAME
from ZConfig.components.logger.loghandler import FileHandler


import logging
import os.path
import time
import zc.lockfile


FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# by default, the audit log will use the same location used for the event log
zopeConf = getConfiguration()

auditlogConf = getattr(
    zopeConf,
    'product_config',
    {}
).get(
    'collective.fingerpointing',
    {}
)

logfile = auditlogConf.get('audit-log', './audit.log')
logger = logging.getLogger(PROJECTNAME)
logger.setLevel(logging.INFO)
logger.info('Start logging audit information to ' + AUDITLOG)

if logfile is not None:
    # Use the rotatingfilehandler to rotate at X Bytes,
    # maxBytes can be 0 to never rotate.
    maxBytes = int(auditlogConf.get('audit-log-max-size', 0))
    backupCount = int(auditlogConf.get('audit-log-old-files', 30))
    handler = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=maxBytes, backupCount=backupCount)

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
