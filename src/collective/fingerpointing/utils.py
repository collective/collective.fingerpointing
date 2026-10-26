from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from file_read_backwards import FileReadBackwards
from glob import glob
from plone import api
from plone.api.exc import CannotGetPortalError
from zope.globalrequest import getRequest
from zope.interface.interfaces import ComponentLookupError

import os


def audit_enabled(setting):
    """Return True if auditing is enabled for this control panel setting,
    e.g. 'audit_pas'.

    Return False while there is no Plone site, like when adding a site or
    adding users from the command line, and when the package is not
    installed.
    """
    name = IFingerPointingSettings.__identifier__ + '.' + setting
    try:
        return api.portal.get_registry_record(name, default=False)
    except (CannotGetPortalError, ComponentLookupError):
        return False


def get_request_information():
    """Return logged in user name and remote IP address."""
    request = getRequest()
    try:
        user_id = api.user.get_current().getMemberId()
    except (AttributeError, CannotGetPortalError):
        user_id = '-'  # anonymous user, or no Plone site

    if request is None:  # e.g. scripts run with zconsole
        return user_id, '-'

    # honor Cloudflare real client IP address request header if present
    # see: https://support.cloudflare.com/hc/en-us/articles/200170986
    if 'HTTP_CF_CONNECTING_IP' in request.environ:
        ip = request.environ['HTTP_CF_CONNECTING_IP']
    # Common proxy configuration
    elif 'HTTP_X_FORWARDED_FOR' in request.environ:
        ip = request.environ['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.getClientAddr() or 'None'  # return 'None' on tests

    return user_id, ip


def audit_log_files():
    """Return a list with the current audit log and all of its
    backups. The list is sorted with newer files first.
    """
    logfiles = []
    if log_info.has_log_file:
        # retrieve the list of audit log backup files
        logfiles = sorted(
            [f for f in glob(log_info.logfile + '.*') if '.lock' not in f],
            reverse=True,
        )
        # include active audit log as first element
        if os.path.exists(log_info.logfile):
            logfiles.insert(0, log_info.logfile)
    return logfiles


def audit_log_lines_of(logfile):
    """Generator for log lines of a log file reversed.
    """
    with FileReadBackwards(logfile, encoding='utf-8') as frb:
        for line in frb:
            yield line.strip()


def all_audit_log_lines():
    """Generator for all lines in the audit logs.

    - Newest file first
    - File is read reversed (backwards)
    """
    for logfile in audit_log_files():
        yield from audit_log_lines_of(logfile)
