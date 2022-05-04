# -*- coding: utf-8 -*-
"""Event subscriber handler for IProfileImportedEvent."""
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api

try:
    # Plone 5.1+
    from zope.interface.interfaces import ComponentLookupError
except ImportError:
    # BBB Plone 5.0-
    from zope.component.interfaces import ComponentLookupError


def profile_imports_logger(event):
    """Log Generic Setup profile imports."""
    name = IFingerPointingSettings.__identifier__ + '.audit_profile_imports'
    try:
        audit_enabled = api.portal.get_registry_record(name, default=False)
    except ComponentLookupError:  # adding Plone site
        return

    if not audit_enabled:
        return

    try:
        user, ip = get_request_information()
    except AttributeError:
        # XXX: getRequest() returns None instead actual request
        #      on tests of this subscriber
        user, ip = '-', '-'

    info = event.tool.getProfileInfo(event.profile_id)
    action = 'profile imported'
    extras = 'id={0} version={1}'.format(
        info['id'],
        info.get('version', '-'),  # uninstall profiles have no version info
    )
    log_info(AUDIT_MESSAGE.format(user, ip, action, extras))
