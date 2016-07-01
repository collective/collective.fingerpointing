# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api
from plone.api.exc import InvalidParameterError
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent
from Products.PluggableAuthService.interfaces.events import IPrincipalDeletedEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedOutEvent


def pas_logger(event):
    """Log authentication events like users logging in and loggin out."""
    # subscriber is registered even if package has not yet been installed
    # ignore any error caused by missing registry records
    try:
        record = IFingerPointingSettings.__identifier__ + '.audit_pas'
        audit_pas = api.portal.get_registry_record(record)
    except InvalidParameterError:
        return

    if audit_pas:
        user, ip = get_request_information()

        if IUserLoggedInEvent.providedBy(event):
            action = 'login'
            extras = ''
        elif IUserLoggedOutEvent.providedBy(event):
            action = 'logout'
            extras = ''
        elif IPrincipalCreatedEvent.providedBy(event):
            action = 'create'
            extras = u'principal={0}'.format(event.principal)
        elif IPrincipalDeletedEvent.providedBy(event):
            action = 'remove'
            extras = u'principal={0}'.format(event.principal)

        log_info(AUDIT_MESSAGE.format(user, ip, action, extras))
