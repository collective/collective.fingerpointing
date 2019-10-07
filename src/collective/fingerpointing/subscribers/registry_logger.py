# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api
from plone.registry.interfaces import IRecordModifiedEvent

import six


def _safe_native_string(s):
    if six.PY2 and isinstance(s, six.text_type):
        s = s.encode('utf-8')
    return s


def registry_logger(event):
    """Log registry events like records being modified."""
    name = IFingerPointingSettings.__identifier__ + '.audit_registry'
    audit_registry = api.portal.get_registry_record(name, default=False)
    if not audit_registry:
        return

    user, ip = get_request_information()

    if IRecordModifiedEvent.providedBy(event):
        action = 'modify'
        extras = 'object={0} value={1}'.format(
            event.record,
            _safe_native_string(event.record.value),
        )
    else:  # should never happen
        action = '-'
        extras = 'object' + event.record

    log_info(AUDIT_MESSAGE.format(user, ip, action, extras))
