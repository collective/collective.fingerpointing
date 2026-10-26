from collective.fingerpointing import _
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface.interfaces import IObjectEvent


class IBrowserLayer(Interface):

    """A layer specific for this add-on product."""


class IFingerPointingSettings(Interface):

    """Schema for the control panel form."""

    audit_pas = schema.Bool(
        title=_('Audit Authentication Service?'),
        description=_(
            'Log authentication events like users logging in and loggin out, '
            'failed logins, password changes and group membership changes.'),
        default=True,
    )

    audit_roles = schema.Bool(
        title=_('Audit Role Assignments?'),
        description=_(
            'Log changes to the global roles of users and groups, '
            'and to local roles on content (sharing).'),
        default=True,
    )

    audit_lifecycle = schema.Bool(
        title=_('Audit Content Type Life Cycle?'),
        description=_(
            'Log content type life cycle events like object creation, modification and removal.'),  # noqa: E501
        default=True,
    )

    audit_workflow = schema.Bool(
        title=_('Audit Workflow Transitions?'),
        description=_('Log workflow transitions like object publishing.'),
        default=True,
    )

    audit_profile_imports = schema.Bool(
        title=_('Audit Profile Imports?'),
        description=_(
            'Log Generic Setup profile imports; '
            'this is useful to audit add-on installs/uninstalls.',
        ),
        default=True,
    )

    audit_registry = schema.Bool(
        title=_('Audit Registry?'),
        description=_('Log registry events like records being modified.'),
        default=True,
    )

    audit_iterate = schema.Bool(
        title=_('Audit Iterate?'),
        description=_(
            'If plone.app.iterate is installed, '
            'log events like content editing checkouts and checkins.'),
        default=True,
    )


class IPrincipalRolesModifiedEvent(Interface):

    """The global roles of a user or group have been changed.

    PAS does not notify this itself; it is fired by this package.
    """

    principal_id = Attribute('Id of the user or group')
    old_roles = Attribute('Roles before the change')
    new_roles = Attribute('Roles after the change')


class ILocalRolesModifiedEvent(IObjectEvent):

    """The local roles of a user or group on an object have been changed.

    Fired by this package for changes made through the sharing view,
    both in Classic UI and through the ``@sharing`` REST API endpoint;
    unlike ``LocalrolesModifiedEvent`` of plone.app.workflow, it tells what
    has changed.
    """

    principal_id = Attribute('Id of the user or group')
    old_roles = Attribute('Local roles before the change')
    new_roles = Attribute('Local roles after the change')


class ILocalRolesInheritanceModifiedEvent(IObjectEvent):

    """Inheritance of local roles has been switched on or off for an object."""

    inherit = Attribute('True if local roles are inherited from the parent')
