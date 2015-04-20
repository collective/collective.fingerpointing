# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.config import BASE_REGISTRY
from collective.fingerpointing.logger import logger
from collective.fingerpointing.utils import get_request_information
from plone import api
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent
from Products.PluggableAuthService.interfaces.events import IPrincipalDeletedEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedOutEvent


def pas_logger(event):
    """Log authentication events like users logging in and loggin out."""
    if api.portal.get_registry_record(BASE_REGISTRY + 'audit_pas'):
        user, ip = get_request_information()

        if IUserLoggedInEvent.providedBy(event):
            action = 'logged in'
            extras = ''
        elif IUserLoggedOutEvent.providedBy(event):
            action = 'logged out'
            extras = ''
        elif IPrincipalCreatedEvent.providedBy(event):
            action = 'user created'
            extras = 'object={0}'.format(event.principal)
        elif IPrincipalDeletedEvent.providedBy(event):
            action = 'user removed'
            extras = 'object={0}'.format(event.principal)

        logger.info(AUDIT_MESSAGE.format(user, ip, action, extras))
