# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api
from Products.PluggableAuthService.interfaces.events import IGroupDeletedEvent
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent  # noqa: E501
from Products.PluggableAuthService.interfaces.events import IPrincipalDeletedEvent  # noqa: E501
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedOutEvent

try:
    # Plone 5.1+
    from zope.interface.interfaces import ComponentLookupError
except ImportError:
    # BBB Plone 5.0-
    from zope.component.interfaces import ComponentLookupError


def pas_logger(event):
    """Log authentication events like users logging in and loggin out."""
    name = IFingerPointingSettings.__identifier__ + '.audit_pas'
    try:
        audit_pas = api.portal.get_registry_record(name, default=False)
    except ComponentLookupError:  # plonectl adduser
        return

    if not audit_pas:
        return

    user, ip = get_request_information()

    if IUserLoggedInEvent.providedBy(event):
        action = 'login'
        extras = ''
    elif IUserLoggedOutEvent.providedBy(event):
        action = 'logout'
        extras = ''
    elif IPrincipalCreatedEvent.providedBy(event):
        action = 'create'
        extras = 'principal=' + str(event.principal)
    elif IPrincipalDeletedEvent.providedBy(event):
        action = 'remove'
        extras = 'user=' + str(event.principal)
    elif IGroupDeletedEvent.providedBy(event):
        action = 'remove'
        extras = 'group=' + str(event.principal)
    else:  # should never happen
        action = 'UNKNOWN'
        extras = ''

    log_info(AUDIT_MESSAGE.format(user, ip, action, extras))
