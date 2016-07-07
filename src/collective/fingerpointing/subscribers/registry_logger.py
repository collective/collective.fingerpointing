# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api
from plone.api.exc import InvalidParameterError
from plone.registry.interfaces import IRecordModifiedEvent


def registry_logger(event):
    """Log registry events like records being modified."""
    # subscriber is registered even if package has not yet been installed
    # ignore any error caused by missing registry records
    try:
        record = IFingerPointingSettings.__identifier__ + '.audit_registry'
        audit_registry = api.portal.get_registry_record(record)
    except InvalidParameterError:
        return

    if audit_registry:
        user, ip = get_request_information()

        if IRecordModifiedEvent.providedBy(event):
            action = 'modify'
            extras = u'object={0} value={1}'.format(event.record, event.record.value)

        log_info(AUDIT_MESSAGE.format(user, ip, action, extras))
