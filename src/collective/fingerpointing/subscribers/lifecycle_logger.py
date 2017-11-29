# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api
from zope.component import ComponentLookupError
from zope.lifecycleevent import IObjectAddedEvent
from zope.lifecycleevent import IObjectModifiedEvent
from zope.lifecycleevent import IObjectRemovedEvent


def lifecycle_logger(obj, event):
    """Log content type life cycle events like object creation,
    modification and removal.
    """
    name = IFingerPointingSettings.__identifier__ + '.audit_lifecycle'
    try:
        audit_lifecycle = api.portal.get_registry_record(name, default=False)
    except ComponentLookupError:  # Plone site removed
        return

    if not audit_lifecycle:
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

    extras = 'object=' + repr(obj)
    log_info(AUDIT_MESSAGE.format(user, ip, action, extras))
