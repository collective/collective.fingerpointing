from collective.fingerpointing import _
from zope.interface import Interface
from zope.schema import Bool


class IBrowserLayer(Interface):
    """A layer specific for this add-on product."""


class IFingerPointingSettings(Interface):
    """Schema for the control panel form."""

    audit_pas = Bool(
        title=_("Audit Authentication Service?"),
        description=_(
            "Log authentication events like users logging in and loggin out."
        ),  # noqa: E501
        default=True,
        required=False,
    )

    audit_lifecycle = Bool(
        title=_("Audit Content Type Life Cycle?"),
        description=_(
            "Log content type life cycle events like object creation, modification and removal."
        ),  # noqa: E501
        default=True,
        required=False,
    )

    audit_workflow = Bool(
        title=_("Audit Workflow Transitions?"),
        description=_("Log workflow transitions like object publishing."),
        default=True,
        required=False,
    )

    audit_profile_imports = Bool(
        title=_("Audit Profile Imports?"),
        description=_(
            "Log Generic Setup profile imports; "
            "this is useful to audit add-on installs/uninstalls.",
        ),
        default=True,
        required=False,
    )

    audit_registry = Bool(
        title=_("Audit Registry?"),
        description=_("Log registry events like records being modified."),
        default=True,
        required=False,
    )

    audit_iterate = Bool(
        title=_("Audit Iterate?"),
        description=_(
            "If plone.app.iterate is installed, "
            "log events like content editing checkouts and checkins."
        ),
        default=True,
        required=False,
    )
