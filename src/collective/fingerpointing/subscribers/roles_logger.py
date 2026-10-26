"""Event subscriber handlers for role changes, see patches.py."""
from collective.fingerpointing.interfaces import ILocalRolesInheritanceModifiedEvent  # noqa: E501
from collective.fingerpointing.interfaces import ILocalRolesModifiedEvent
from collective.fingerpointing.interfaces import IPrincipalRolesModifiedEvent
from collective.fingerpointing.logger import AuditList
from collective.fingerpointing.logger import AuditObject
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import audit_enabled
from collective.fingerpointing.utils import get_request_information


def roles_logger(event):
    """Log changes to global roles and to local roles on content."""
    if not audit_enabled('audit_roles'):
        return

    if IPrincipalRolesModifiedEvent.providedBy(event):
        action = 'roles change'
        details = [
            ('principal', event.principal_id),
            ('roles', AuditList(sorted(event.new_roles))),
            ('old_roles', AuditList(sorted(event.old_roles))),
        ]
    elif ILocalRolesModifiedEvent.providedBy(event):
        action = 'local roles change'
        details = [
            ('object', AuditObject(event.object)),
            ('principal', event.principal_id),
            ('roles', AuditList(sorted(event.new_roles))),
            ('old_roles', AuditList(sorted(event.old_roles))),
        ]
    elif ILocalRolesInheritanceModifiedEvent.providedBy(event):
        action = 'local roles inheritance'
        details = [
            ('object', AuditObject(event.object)),
            ('inherit', event.inherit),
        ]
    else:  # should never happen
        return

    user, ip = get_request_information()
    log_info.audit(user, ip, action, details)
