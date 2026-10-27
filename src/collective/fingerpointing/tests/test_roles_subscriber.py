"""Tests for role change subscribers."""
from collective.fingerpointing import patches
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.testing import FUNCTIONAL_TESTING
from collective.fingerpointing.testing import INTEGRATION_TESTING
from collective.fingerpointing.testing import UninstallMixin
from logging import INFO
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser
from testfixtures import LogCapture

import json
import transaction
import unittest


class RolesSubscribersTestCase(unittest.TestCase, UninstallMixin):
    """Tests for global and local role changes."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.user.create(username='bob', email='bob@example.org')
        api.group.create(groupname='staff')
        self.folder = api.content.create(self.portal, 'Folder', 'folder')
        # only show the events of these tests
        name = IFingerPointingSettings.__identifier__ + '.audit_lifecycle'
        api.portal.set_registry_record(name, False)

    def test_global_roles_user(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            api.user.grant_roles(username='bob', roles=['Site Administrator'])
            api.user.revoke_roles(username='bob', roles=['Site Administrator'])
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=roles change principal=bob roles=Member,Site Administrator old_roles=Member'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=roles change principal=bob roles=Member old_roles=Member,Site Administrator'),  # noqa: E501
            )

    def test_global_roles_group(self):
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            api.group.grant_roles(groupname='staff', roles=['Editor'])
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=roles change principal=staff roles=Editor old_roles='),  # noqa: E501
            )

    def test_role_manager_methods(self):
        plugin = self.portal.acl_users.portal_role_manager
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            plugin.assignRoleToPrincipal('Reviewer', 'bob')
            plugin.assignRoleToPrincipal('Reviewer', 'bob')  # no change
            plugin.removeRoleFromPrincipal('Reviewer', 'bob')
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=roles change principal=bob roles=Member,Reviewer old_roles=Member'),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=roles change principal=bob roles=Member old_roles=Member,Reviewer'),  # noqa: E501
            )

    @unittest.skipIf(
        patches.IRoleAssignedToPrincipalEvent is None,
        'Products.PluggableAuthService < 4.3 fires no role events')
    def test_pas_role_events(self):
        from Products.PlonePAS.plugins.role import GroupAwareRoleManager
        from Products.PluggableAuthService.events import RoleAssignedToPrincipal  # noqa: E501
        from zope.event import notify

        # PAS fires the events: no need to patch these methods
        for name in ('assignRoleToPrincipal', 'removeRoleFromPrincipal'):
            method = getattr(GroupAwareRoleManager, name)
            self.assertFalse(hasattr(method, '__wrapped__'), name)
        # PlonePAS sets all roles at once, without them
        self.assertTrue(
            hasattr(GroupAwareRoleManager.assignRolesToPrincipal, '__wrapped__'))

        # an event of another role manager than the one of the site
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            notify(RoleAssignedToPrincipal('bob', 'Reviewer'))
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=roles change principal=bob roles=Reviewer old_roles='),  # noqa: E501
            )

    def test_local_roles(self):
        view = self.folder.restrictedTraverse('@@sharing')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            view.update_role_settings([
                {'id': 'bob', 'type': 'user', 'roles': ['Editor', 'Reader']},
                {'id': 'staff', 'type': 'group', 'roles': ['Reader']},
            ])
            view.update_role_settings([
                {'id': 'bob', 'type': 'user', 'roles': []},
            ])
            log.check(
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=local roles change object=<Folder at /plone/folder> principal=bob roles=Editor,Reader old_roles='),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=local roles change object=<Folder at /plone/folder> principal=staff roles=Reader old_roles='),  # noqa: E501
                ('collective.fingerpointing', 'INFO', 'user=test_user_1_ ip=None action=local roles change object=<Folder at /plone/folder> principal=bob roles= old_roles=Editor,Reader'),  # noqa: E501
            )

    def test_local_roles_unchanged(self):
        view = self.folder.restrictedTraverse('@@sharing')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            view.update_role_settings([
                {'id': 'bob', 'type': 'user', 'roles': []},
            ])
            log.check()

    def test_local_roles_inheritance(self):
        # blocking inheritance gives the current user the local roles
        # it inherited, so it does not lock itself out
        self.portal.manage_setLocalRoles(TEST_USER_ID, ['Editor'])
        view = self.folder.restrictedTraverse('@@sharing')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            view.update_inherit(False)
            view.update_inherit(True)
        actions = [r.getMessage().split(' action=')[1] for r in log.records]
        self.assertEqual(actions, [
            'local roles change object=<Folder at /plone/folder> principal=test_user_1_ roles=Editor,Owner old_roles=Owner',  # noqa: E501
            'local roles inheritance object=<Folder at /plone/folder> inherit=False',  # noqa: E501
            'local roles inheritance object=<Folder at /plone/folder> inherit=True',  # noqa: E501
        ])

    def test_disabled(self):
        name = IFingerPointingSettings.__identifier__ + '.audit_roles'
        api.portal.set_registry_record(name, False)
        view = self.folder.restrictedTraverse('@@sharing')
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            api.user.grant_roles(username='bob', roles=['Editor'])
            view.update_role_settings([
                {'id': 'bob', 'type': 'user', 'roles': ['Editor']},
            ])
            log.check()

    def test_susbcriber_ignored_when_package_not_installed(self):
        self.uninstall()
        view = self.folder.restrictedTraverse('@@sharing')
        api.user.grant_roles(username='bob', roles=['Editor'])
        view.update_role_settings([
            {'id': 'bob', 'type': 'user', 'roles': ['Editor']},
        ])
        view.update_inherit(False)


class SharingAPITestCase(unittest.TestCase):
    """Volto changes local roles through the @sharing endpoint."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        api.user.create(username='bob', email='bob@example.org')
        with api.env.adopt_roles(['Manager']):
            api.content.create(self.portal, 'Folder', 'folder')
        name = IFingerPointingSettings.__identifier__ + '.audit_lifecycle'
        api.portal.set_registry_record(name, False)
        transaction.commit()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader('Accept', 'application/json')
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}',
        )

    def test_sharing_endpoint(self):
        data = {
            'entries': [{
                'id': 'bob',
                'type': 'user',
                'roles': {'Editor': True, 'Reader': False},
            }],
            'inherit': False,
        }
        with LogCapture('collective.fingerpointing', level=INFO) as log:
            self.browser.post(
                self.portal.absolute_url() + '/folder/@sharing',
                json.dumps(data),
                'application/json',
            )
        actions = [r.getMessage().split(' action=')[1] for r in log.records]
        self.assertIn(
            'local roles change object=<Folder at /plone/folder> principal=bob roles=Editor old_roles=',  # noqa: E501
            actions,
        )
        self.assertIn(
            'local roles inheritance object=<Folder at /plone/folder> inherit=False',  # noqa: E501
            actions,
        )
        users = [r.getMessage().split(' ')[0] for r in log.records]
        self.assertEqual(set(users), {'user=admin'})
