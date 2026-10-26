from collective.fingerpointing.logger import AuditObject
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import audit_enabled
from collective.fingerpointing.utils import get_request_information
from plone.app.iterate.interfaces import ICancelCheckoutEvent
from plone.app.iterate.interfaces import ICheckinEvent
from plone.app.iterate.interfaces import ICheckoutEvent


def iterate_logger(event):
    """Log events like content editing checkouts and checkins, if
    plone.app.iterate is installed.
    """
    if not audit_enabled('audit_iterate'):
        return

    user, ip = get_request_information()

    def ref(obj):
        return AuditObject(obj, text=str)

    if ICheckoutEvent.providedBy(event):
        action = 'checkout'
        details = [
            ('object', ref(event.object)),
            ('working_copy', ref(event.working_copy)),
        ]
    elif ICheckinEvent.providedBy(event):
        action = 'checkin'
        details = [
            ('object', ref(event.object)),
            ('baseline', ref(event.baseline)),
        ]
    elif ICancelCheckoutEvent.providedBy(event):
        action = 'cancel checkout'
        details = [
            ('object', ref(event.object)),
            ('baseline', ref(event.baseline)),
        ]
    else:  # should never happen
        action = '-'
        details = [('object', AuditObject(event.object))]

    log_info.audit(user, ip, action, details)
