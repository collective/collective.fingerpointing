"""Tests for PluggableAuthService subscribers."""
from collective.fingerpointing.testing import FUNCTIONAL_TESTING
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import UninstallMixin
from logging import INFO
from plone import api
from plone.app.testing import logout
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.zope import Browser
from Products.PlonePAS.events import UserLoggedInEvent
from Products.PlonePAS.events import UserLoggedOutEvent
from Products.PluggableAuthService.events import GroupCreated
from Products.PluggableAuthService.events import GroupDeleted
from Products.PluggableAuthService.events import PrincipalCreated
from Products.PluggableAuthService.events import PrincipalDeleted
from testfixtures import LogCapture
from zope.event import notify
from ZPublisher.pubevents import PubAfterTraversal

import json
import transaction
import unittest


class PasSubscribersTestCase(unittest.TestCase, UninstallMixin):
    """Tests for PluggableAuthService subscribers."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_user_login(self):
        event = UserLoggedInEvent(self.request)
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=login '),  # noqa: E501
            )

    def test_user_logout(self):
        event = UserLoggedOutEvent(self.request)
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=logout '),  # noqa: E501
            )

    def test_user_created(self):
        event = PrincipalCreated('foo')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create principal=foo'),  # noqa: E501
            )

    def test_user_removed(self):
        event = PrincipalDeleted('foo')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove user=foo'),  # noqa: E501
            )

    def test_group_removed(self):
        event = GroupDeleted('bar')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove group=bar'),  # noqa: E501
            )

    def test_group_created(self):
        event = GroupCreated('bar', None)
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(event)
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=create group=bar'),  # noqa: E501
            )

    def test_group_membership(self):
        api.user.create(username='bob', email='bob@example.org')
        api.group.create(groupname='staff')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            api.group.add_user(groupname='staff', username='bob')
            api.group.remove_user(groupname='staff', username='bob')
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=add to group principal=bob group=staff'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=remove from group principal=bob group=staff'),  # noqa: E501
            )

    def test_password_change(self):
        api.user.create(username='bob', email='bob@example.org')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.portal.acl_users.userSetPassword('bob', 'S3cret!passw0rd')
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=password change principal=bob'),  # noqa: E501
            )
        # never log the password
        self.assertNotIn('S3cret', str(log))

    def test_properties_change(self):
        user = api.user.create(username='bob', email='bob@example.org')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            user.setMemberProperties(
                {'email': 'robert@example.org', 'fullname': 'Robert'})
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=properties change principal=bob properties=email,fullname'),  # noqa: E501
            )
        # only the names of the properties, not their values
        self.assertNotIn('robert@example.org', str(log))

    def test_login_time_properties_ignored(self):
        user = api.user.create(username='bob', email='bob@example.org')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            user.setMemberProperties({
                'login_time': '2026-10-26',
                'last_login_time': '2026-10-25',
            })
            log.check()

    def test_failed_login(self):
        logout()
        self.request.form['__ac_name'] = 'bob'
        self.request.form['__ac_password'] = 'wrong'
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(PubAfterTraversal(self.request))
            log.check(
                ('collective.fingerpointing', 'WARNING', 'user=- ip=None action=login failed login=bob'),  # noqa: E501
            )

    def test_successful_login_not_logged_as_failed(self):
        # the credentials were valid: the user is authenticated
        self.request.form['__ac_name'] = TEST_USER_NAME
        self.request.form['__ac_password'] = TEST_USER_PASSWORD
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(PubAfterTraversal(self.request))
            log.check()

    def test_request_without_credentials_ignored(self):
        logout()
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(PubAfterTraversal(self.request))
            log.check()

    def test_susbcriber_ignored_when_package_not_installed(self):
        # authentication events should not raise errors
        # if package is not installed
        self.uninstall()

        event = UserLoggedInEvent(self.request)
        notify(event)
        event = UserLoggedOutEvent(self.request)
        notify(event)
        event = PrincipalCreated('foo')
        notify(event)
        event = PrincipalDeleted('foo')
        notify(event)


class LoginTestCase(unittest.TestCase):
    """Log in through the Classic UI login form and the REST API."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        api.user.create(
            username='bob', email='bob@example.org', password='S3cret!passw0rd')
        transaction.commit()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.raiseHttpErrors = False

    def actions(self, log):
        return [
            (r.levelname, r.getMessage().split(' action=')[1])
            for r in log.records
        ]

    def login_form(self, login, password):
        self.browser.open(self.portal_url + '/login')
        self.browser.getControl(name='__ac_name').value = login
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='buttons.login').click()

    def api_login(self, login, password):
        self.browser.addHeader('Accept', 'application/json')
        self.browser.post(
            self.portal_url + '/@login',
            json.dumps({'login': login, 'password': password}),
            'application/json',
        )

    def test_login_form(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.login_form('bob', 'S3cret!passw0rd')
        self.assertEqual(self.actions(log), [('INFO', 'login ')])

    def test_login_form_failed(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.login_form('bob', 'wrong')
        self.assertEqual(
            self.actions(log), [('WARNING', 'login failed login=bob')])

    def test_api_login(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.api_login('bob', 'S3cret!passw0rd')
        self.assertEqual(self.browser.headers['status'], '200 OK')
        self.assertEqual(self.actions(log), [('INFO', 'login ')])

    def test_api_login_failed(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.api_login('bob', 'wrong')
        self.assertEqual(self.browser.headers['status'], '401 Unauthorized')
        self.assertEqual(
            self.actions(log), [('WARNING', 'login failed login=bob')])

    def test_api_login_failed_unknown_user(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.api_login('nobody', 'wrong')
        self.assertEqual(
            self.actions(log), [('WARNING', 'login failed login=nobody')])

    def test_api_login_site_owner(self):
        # a user from the Zope root user folder
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.api_login(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.assertNotIn('login failed', str(log))
