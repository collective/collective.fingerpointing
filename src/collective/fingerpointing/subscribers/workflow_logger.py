"""Event subscriber handler for IActionSucceededEvent."""
from collective.fingerpointing.logger import AuditObject
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import audit_enabled
from collective.fingerpointing.utils import get_request_information


def workflow_logger(event):
    """Log workflow transitions."""
    if not audit_enabled('audit_workflow'):
        return

    user, ip = get_request_information()

    action = 'workflow transition'
    details = [
        ('object', AuditObject(event.object)),
        ('transition', event.action),
    ]
    log_info.audit(user, ip, action, details)
