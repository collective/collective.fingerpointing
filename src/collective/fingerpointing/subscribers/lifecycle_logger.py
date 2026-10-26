from collective.fingerpointing.logger import AuditObject
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import audit_enabled
from collective.fingerpointing.utils import get_request_information
from zope.lifecycleevent import IObjectAddedEvent
from zope.lifecycleevent import IObjectModifiedEvent
from zope.lifecycleevent import IObjectRemovedEvent


def lifecycle_logger(obj, event):
    """Log content type life cycle events like object creation,
    modification and removal.
    """
    if not audit_enabled('audit_lifecycle'):
        return

    user, ip = get_request_information()

    if IObjectAddedEvent.providedBy(event):
        action = 'create'
    elif IObjectModifiedEvent.providedBy(event):
        action = 'modify'
    elif IObjectRemovedEvent.providedBy(event):
        action = 'remove'
    else:  # should never happen
        action = '-'

    log_info.audit(user, ip, action, [('object', AuditObject(obj))])
