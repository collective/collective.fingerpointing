from AccessControl import getSecurityManager
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import audit_enabled
from collective.fingerpointing.utils import get_request_information
from Products.PluggableAuthService.interfaces.events import ICredentialsUpdatedEvent  # noqa: E501
from Products.PluggableAuthService.interfaces.events import IGroupCreatedEvent
from Products.PluggableAuthService.interfaces.events import IGroupDeletedEvent
from Products.PluggableAuthService.interfaces.events import IPrincipalAddedToGroupEvent  # noqa: E501
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent  # noqa: E501
from Products.PluggableAuthService.interfaces.events import IPrincipalDeletedEvent  # noqa: E501
from Products.PluggableAuthService.interfaces.events import IPrincipalRemovedFromGroupEvent  # noqa: E501
from Products.PluggableAuthService.interfaces.events import IPropertiesUpdatedEvent  # noqa: E501
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedOutEvent

import json
import logging


# PlonePAS updates these on every login; that is not a change to audit
LOGIN_PROPERTIES = frozenset(['login_time', 'last_login_time'])


def principal_id(principal):
    """Return the id of a principal, which events pass as an object or id."""
    if isinstance(principal, str):
        return principal
    get_id = getattr(principal, 'getId', None)
    if get_id is not None:
        return get_id()
    return str(principal)


def pas_logger(event):
    """Log authentication events like users logging in and loggin out."""
    if not audit_enabled('audit_pas'):
        return

    if IUserLoggedInEvent.providedBy(event):
        action = 'login'
        details = []
    elif IUserLoggedOutEvent.providedBy(event):
        action = 'logout'
        details = []
    elif IPrincipalCreatedEvent.providedBy(event):
        action = 'create'
        details = [('principal', str(event.principal))]
    elif IGroupCreatedEvent.providedBy(event):
        action = 'create'
        details = [('group', principal_id(event.principal))]
    elif IPrincipalDeletedEvent.providedBy(event):
        action = 'remove'
        details = [('user', str(event.principal))]
    elif IGroupDeletedEvent.providedBy(event):
        action = 'remove'
        details = [('group', str(event.principal))]
    elif IPrincipalAddedToGroupEvent.providedBy(event):
        action = 'add to group'
        details = [
            ('principal', principal_id(event.principal)),
            ('group', event.group_id),
        ]
    elif IPrincipalRemovedFromGroupEvent.providedBy(event):
        action = 'remove from group'
        details = [
            ('principal', principal_id(event.principal)),
            ('group', event.group_id),
        ]
    elif ICredentialsUpdatedEvent.providedBy(event):
        # never log event.password
        action = 'password change'
        details = [('principal', principal_id(event.principal))]
    elif IPropertiesUpdatedEvent.providedBy(event):
        names = set(event.properties or ()) - LOGIN_PROPERTIES
        if not names:
            return
        # only the names; the values may be personal data
        action = 'properties change'
        details = [
            ('principal', principal_id(event.principal)),
            ('properties', ','.join(sorted(names))),
        ]
    else:  # should never happen
        action = 'UNKNOWN'
        details = []

    user, ip = get_request_information()
    log_info.audit(user, ip, action, details)


def log_failed_login(login):
    if not audit_enabled('audit_pas'):
        return
    user, ip = get_request_information()
    log_info.audit(
        user, ip, 'login failed', [('login', login)], level=logging.WARNING)


def failed_login_logger(event):
    """Log failed logins through the Classic UI login form, and any other
    request that posts ``__ac_name`` and ``__ac_password``.

    Those credentials are checked while traversing: if they are valid,
    the user is authenticated after traversal; if not, the user is anonymous.
    """
    request = event.request
    form = getattr(request, 'form', None) or {}
    login = form.get('__ac_name')
    if not login or not form.get('__ac_password'):
        return
    user = getSecurityManager().getUser()
    if user is None or user.getUserName() == 'Anonymous User':
        log_failed_login(login)


def failed_api_login_logger(event):
    """Log failed logins through the plone.restapi ``@login`` endpoint,
    which Volto uses: it answers 401 Unauthorized without raising an error.
    """
    request = event.request
    if request.get('REQUEST_METHOD') != 'POST':
        return
    if not request.get('PATH_INFO', '').endswith('/@login'):
        return
    if request.response.getStatus() != 401:
        return
    try:
        login = json.loads(request.get('BODY') or b'{}').get('login')
    except (ValueError, AttributeError):
        login = None
    log_failed_login(login or '-')
