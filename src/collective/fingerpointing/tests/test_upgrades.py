# -*- coding: utf-8 -*-
from collective.fingerpointing.testing import INTEGRATION_TESTING
from plone import api

import unittest


class BaseUpgradeTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING
    profile_id = u'collective.fingerpointing:default'

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup = self.portal['portal_setup']
        self.setup.setLastVersionForProfile(self.profile_id, self.from_)

    def _get_upgrade_step_by_title(self, title):
        """Return the upgrade step that matches the title specified."""
        self.setup.setLastVersionForProfile(self.profile_id, self.from_)
        upgrades = self.setup.listUpgrades(self.profile_id)
        steps = [s for s in upgrades[0] if s['title'] == title]
        return steps[0] if steps else None

    def _do_upgrade(self, step):
        """Execute an upgrade step."""
        request = self.layer['request']
        request.form['profile_id'] = self.profile_id
        request.form['upgrades'] = [step['id']]
        self.setup.manage_doUpgrades(request=request)


class To2TestCase(BaseUpgradeTestCase):

    from_ = '1'
    to_ = '2'

    def test_profile_version(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertEqual(version, self.from_)

    def test_registered_steps(self):
        steps = len(self.setup.listUpgrades(self.profile_id)[0])
        self.assertEqual(steps, 2)

    def test_update_configlet(self):
        # check if the upgrade step is registered
        title = u'Update control panel configlet'
        step = self._get_upgrade_step_by_title(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        cptool = api.portal.get_tool('portal_controlpanel')
        configlet = cptool.getActionObject('Products/fingerpointing')
        configlet.permissions = old_permissions = ('cmf.ManagePortal',)
        self.assertEqual(configlet.getPermissions(), old_permissions)

        # run the upgrade step to validate the update
        self._do_upgrade(step)
        configlet = cptool.getActionObject('Products/fingerpointing')
        new_permissions = ('collective.fingerpointing: Setup',)
        self.assertEqual(configlet.getPermissions(), new_permissions)

    def test_update_user_actions(self):
        # check if the upgrade step is registered
        title = u'Update user actions'
        step = self._get_upgrade_step_by_title(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        permission = 'collective.fingerpointing: View Audit Log'
        self.portal.manage_permission(permission_to_manage=permission, roles=[])
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        self.assertListEqual(roles, [])

        user_actions = self.portal['portal_actions'].user
        del user_actions['audit-log']
        self.assertNotIn('audit-log', user_actions)

        # run the upgrade step to validate the update
        self._do_upgrade(step)
        roles = self.portal.rolesOfPermission(permission)
        roles = [r['name'] for r in roles if r['selected']]
        self.assertListEqual(roles, ['Manager', 'Site Administrator'])

        permissions = user_actions['audit-log'].permissions
        expected = (permission,)
        self.assertEqual(permissions, expected)
        url_expr = user_actions['audit-log'].url_expr
        self.assertIn('/@@fingerpointing-audit-log', url_expr)


class To3TestCase(BaseUpgradeTestCase):

    from_ = '2'
    to_ = '3'

    def test_profile_version(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertEqual(version, self.from_)

    def test_registered_steps(self):
        steps = len(self.setup.listUpgrades(self.profile_id)[0])
        self.assertEqual(steps, 1)

    def test_update_user_actions(self):
        # check if the upgrade step is registered
        title = u'Update user actions'
        step = self._get_upgrade_step_by_title(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        user_actions = self.portal['portal_actions'].user
        user_actions.moveObjectsDown('audit-log')
        self.assertEqual(user_actions.keys()[-1], 'audit-log')
        self.assertEqual(user_actions.keys()[-2], 'logout')

        # run the upgrade step to validate the update
        self._do_upgrade(step)
        self.assertEqual(user_actions.keys()[-1], 'logout')
        self.assertEqual(user_actions.keys()[-2], 'audit-log')
