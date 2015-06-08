# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import logger
from collective.fingerpointing.utils import get_request_information
from plone import api
from plone.registry.interfaces import IRecordModifiedEvent


def registry_logger(event):
    """Log registry events like records being modified."""
    record = IFingerPointingSettings.__identifier__ + '.audit_registry'
    if api.portal.get_registry_record(record):
        user, ip = get_request_information()

        if IRecordModifiedEvent.providedBy(event):
            action = 'record modified'
            extras = 'object={0} value={1}'.format(event.record, event.record.value)

        logger.info(AUDIT_MESSAGE.format(user, ip, action, extras))
