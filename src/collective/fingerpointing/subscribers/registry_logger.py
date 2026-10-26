from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import audit_enabled
from collective.fingerpointing.utils import get_request_information
from plone.registry.interfaces import IRecordModifiedEvent


def registry_logger(event):
    """Log registry events like records being modified."""
    if not audit_enabled('audit_registry'):
        return

    user, ip = get_request_information()

    if IRecordModifiedEvent.providedBy(event):
        action = 'modify'
        details = [
            ('object', event.record),
            ('value', event.record.value),
        ]
    else:  # should never happen
        action = '-'
        details = [('object', event.record)]

    log_info.audit(user, ip, action, details)
