"""Fire events for role changes, which Plone does not notify itself.

- Global roles: every change made through the Users and Groups control panel,
  the ``@users``/``@groups`` REST API endpoints or ``portal_groups`` ends up in
  the role manager plugin of PlonePAS.
- Local roles: the Classic UI sharing view and the ``@sharing`` REST API
  endpoint both use the methods of the sharing view. Both fire
  ``LocalrolesModifiedEvent`` afterwards, but that does not tell what has
  changed.
"""
from collective.fingerpointing.events import LocalRolesInheritanceModifiedEvent  # noqa: E501
from collective.fingerpointing.events import LocalRolesModifiedEvent
from collective.fingerpointing.events import PrincipalRolesModifiedEvent
from contextlib import contextmanager
from functools import wraps
from zope.event import notify

import logging


logger = logging.getLogger('fingerpointing common')

PATCHED = '_fingerpointing_patched'


# every principal has these; plone.api stores them anyway
VIRTUAL_ROLES = frozenset(['Anonymous', 'Authenticated'])


def global_roles(plugin, principal_id):
    roles = plugin._principal_roles.get(principal_id, ())
    return tuple(sorted(set(roles) - VIRTUAL_ROLES))


@contextmanager
def global_roles_change(plugin, principal_id):
    old_roles = global_roles(plugin, principal_id)
    yield
    new_roles = global_roles(plugin, principal_id)
    if old_roles != new_roles:
        notify(PrincipalRolesModifiedEvent(principal_id, old_roles, new_roles))


def local_roles(context):
    return {
        principal_id: tuple(sorted(roles))
        for principal_id, roles in context.get_local_roles()
    }


@contextmanager
def local_roles_change(context):
    old = local_roles(context)
    yield
    new = local_roles(context)
    for principal_id in sorted(set(old) | set(new)):
        old_roles = old.get(principal_id, ())
        new_roles = new.get(principal_id, ())
        if old_roles != new_roles:
            notify(LocalRolesModifiedEvent(
                context, principal_id, old_roles, new_roles))


def patch_role_manager():
    from Products.PlonePAS.plugins.role import GroupAwareRoleManager

    if getattr(GroupAwareRoleManager, PATCHED, False):
        return

    original_assign_role = GroupAwareRoleManager.assignRoleToPrincipal
    original_assign_roles = GroupAwareRoleManager.assignRolesToPrincipal
    original_remove_role = GroupAwareRoleManager.removeRoleFromPrincipal

    @wraps(original_assign_role)
    def assignRoleToPrincipal(self, role_id, principal_id, REQUEST=None):
        with global_roles_change(self, principal_id):
            return original_assign_role(
                self, role_id, principal_id, REQUEST=REQUEST)

    # this one is wrapped by AccessControl's postonly, which needs REQUEST
    @wraps(original_assign_roles)
    def assignRolesToPrincipal(self, roles, principal_id, REQUEST=None):
        with global_roles_change(self, principal_id):
            return original_assign_roles(self, roles, principal_id, REQUEST)

    @wraps(original_remove_role)
    def removeRoleFromPrincipal(self, role_id, principal_id):
        with global_roles_change(self, principal_id):
            return original_remove_role(self, role_id, principal_id)

    GroupAwareRoleManager.assignRoleToPrincipal = assignRoleToPrincipal
    GroupAwareRoleManager.assignRolesToPrincipal = assignRolesToPrincipal
    GroupAwareRoleManager.removeRoleFromPrincipal = removeRoleFromPrincipal
    setattr(GroupAwareRoleManager, PATCHED, True)


def patch_sharing_view():
    from plone.app.workflow.browser.sharing import SharingView

    if getattr(SharingView, PATCHED, False):
        return

    original_update_role_settings = SharingView.update_role_settings
    original_update_inherit = SharingView.update_inherit

    @wraps(original_update_role_settings)
    def update_role_settings(self, new_settings, reindex=True):
        with local_roles_change(self.context):
            return original_update_role_settings(
                self, new_settings, reindex=reindex)

    # blocking inheritance can also set local roles, to keep access
    @wraps(original_update_inherit)
    def update_inherit(self, status=True, reindex=True):
        with local_roles_change(self.context):
            changed = original_update_inherit(
                self, status=status, reindex=reindex)
        if changed:
            notify(LocalRolesInheritanceModifiedEvent(
                self.context, bool(status)))
        return changed

    SharingView.update_role_settings = update_role_settings
    SharingView.update_inherit = update_inherit
    setattr(SharingView, PATCHED, True)


def apply():
    patch_role_manager()
    patch_sharing_view()
    logger.debug('Patched role manager and sharing view to audit role changes')
