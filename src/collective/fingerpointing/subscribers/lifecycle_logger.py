# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api
from plone.api.exc import InvalidParameterError
from zope.component import ComponentLookupError
from zope.lifecycleevent import IObjectCreatedEvent
from zope.lifecycleevent import IObjectModifiedEvent
from zope.lifecycleevent import IObjectRemovedEvent


def lifecycle_logger(obj, event):
    """Log content type life cycle events like object creation,
    modification and removal.
    """
    # subscriber is registered even if package has not yet been installed
    # ignore any error caused by missing registry records
    try:
        record = IFingerPointingSettings.__identifier__ + '.audit_lifecycle'
        audit_lifecycle = api.portal.get_registry_record(record)
    except (ComponentLookupError, InvalidParameterError):
        return

    if audit_lifecycle:
        user, ip = get_request_information()

        if IObjectCreatedEvent.providedBy(event):
            action = 'create'
            extras = u'object={0}'.format(repr(obj))
        if IObjectModifiedEvent.providedBy(event):
            action = 'modify'
            extras = u'object={0}'.format(repr(obj))
        if IObjectRemovedEvent.providedBy(event):
            action = 'remove'
            extras = u'object={0}'.format(repr(obj))

        log_info(AUDIT_MESSAGE.format(user, ip, action, extras))
