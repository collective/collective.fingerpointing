# -*- coding: utf-8 -*-
"""Event subscriber handler for IProfileImportedEvent."""
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api


def profile_imports_logger(event):
    """Log Generic Setup profile imports."""
    name = IFingerPointingSettings.__identifier__ + '.audit_profile_imports'
    audit_profile_imports = api.portal.get_registry_record(name, default=False)
    if not audit_profile_imports:
        return

    try:
        user, ip = get_request_information()
    except AttributeError:
        # XXX: getRequest() returns None instead actual request
        #      on tests of this subscriber
        user, ip = '-', '-'

    info = event.tool.getProfileInfo(event.profile_id)
    action = 'profile imported'
    extras = 'id={id} version={version}'.format(**info)
    log_info(AUDIT_MESSAGE.format(user, ip, action, extras))
