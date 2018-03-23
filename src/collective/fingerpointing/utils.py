# -*- coding: utf-8 -*-
from collective.fingerpointing.logger import log_info
from file_read_backwards import FileReadBackwards
from glob import glob
from plone import api
from zope.globalrequest import getRequest

import os

""" TODO.
    This page ( https://www.garykessler.net/library/file_sigs.html )
    has a list of "magic" file signatures. Grab the ones you need
    and put them in a dict like below.
    Then we need a function that matches the dict keys with the
    start of the file.

    I've written a suggestion, though it can be optimized by
     preprocessing the magic_dict into e.g. one giant compiled regexp
"""
magic_dict = {
    "\x1f\x8b\x08": "gz",
    "\x42\x5a\x68": "bz2",
    "\x50\x4b\x03\x04": "zip"
    }
max_len = max(len(x) for x in magic_dict)


def get_request_information():
    """Return logged in user name and remote IP address."""
    request = getRequest()
    try:
        user_id = api.user.get_current().getMemberId()
    except AttributeError:
        user_id = '-'  # anonymous user

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


def isCompressedFile(filename):
    """ This solution should be cross-plattform and is of course
        not dependent on file name extension, but it may give
        false positives for files with random content that just
        happen to start with some specific magic bytes.
    """
    with open(filename) as f:
        file_start = f.read(max_len)
    for magic, filetype in magic_dict.items():
        if file_start.startswith(magic):
            return (True, filetype)
    return (False, "no match")


def audit_log_files():
    """Return a list with the current audit log and all of its
    backups. The list is sorted with newer files first.
    """
    # retrieve the list of audit log backup files
    logfiles = sorted(
        [f for f in glob(log_info.logfile + '.*') if '.lock' not in f and not isCompressedFile(f)[0]],
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
        for line in audit_log_lines_of(logfile):
            yield line
