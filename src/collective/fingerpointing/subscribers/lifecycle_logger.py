# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.config import BASE_REGISTRY
from collective.fingerpointing.logger import logger
from collective.fingerpointing.utils import get_request_information
from plone import api
from zope.lifecycleevent import IObjectCreatedEvent
from zope.lifecycleevent import IObjectModifiedEvent
from zope.lifecycleevent import IObjectRemovedEvent


def lifecycle_logger(obj, event):
    """Log content type life cycle events like object creation,
    modification and removal.
    """
    if api.portal.get_registry_record(BASE_REGISTRY + 'audit_lifecycle'):
        user, ip = get_request_information()

        if IObjectCreatedEvent.providedBy(event):
            action = 'object created'
            extras = 'object={0}'.format(obj)
        if IObjectModifiedEvent.providedBy(event):
            action = 'object modified'
            extras = 'object={0}'.format(obj)
        if IObjectRemovedEvent.providedBy(event):
            action = 'object removed'
            extras = 'object={0}'.format(obj)

        logger.info(AUDIT_MESSAGE.format(user, ip, action, extras))
