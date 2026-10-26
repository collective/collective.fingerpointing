"""Event subscriber handler for IProfileImportedEvent."""
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import audit_enabled
from collective.fingerpointing.utils import get_request_information


def profile_imports_logger(event):
    """Log Generic Setup profile imports."""
    if not audit_enabled('audit_profile_imports'):
        return

    user, ip = get_request_information()

    info = event.tool.getProfileInfo(event.profile_id)
    action = 'profile imported'
    details = [
        ('id', info['id']),
        # uninstall profiles have no version info
        ('version', info.get('version', '-')),
    ]
    log_info.audit(user, ip, action, details)
