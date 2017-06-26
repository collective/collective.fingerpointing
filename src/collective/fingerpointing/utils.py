# -*- coding: utf-8 -*-
from plone import api
from zope.globalrequest import getRequest


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
