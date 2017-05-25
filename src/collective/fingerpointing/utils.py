# -*- coding: utf-8 -*-
from plone import api
from zope.globalrequest import getRequest


def get_request_information():
    """Return logged in user name and remote IP address."""
    request = getRequest()
    user = api.user.get_current().getMemberId()

    # honor Cloudflare real client IP address request header if present
    # see: https://support.cloudflare.com/hc/en-us/articles/200170986
    if 'HTTP_CF_CONNECTING_IP' in request.environ:
        ip = request.environ['HTTP_CF_CONNECTING_IP']
    else:
        ip = request.getClientAddr() or 'None'

    return user, ip  # returns ('test_user_1_', 'None') on tests
