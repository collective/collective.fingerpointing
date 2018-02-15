# -*- coding: utf-8 -*-
from collective.fingerpointing import _
from zope import schema
from zope.interface import Interface


class IBrowserLayer(Interface):

    """A layer specific for this add-on product."""


class IFingerPointingSettings(Interface):

    """Schema for the control panel form."""

    audit_pas = schema.Bool(
        title=_(u'Audit Authentication Service?'),
        description=_(
            u'Log authentication events like users logging in and loggin out.'),   # noqa: E501
        default=True,
    )

    audit_lifecycle = schema.Bool(
        title=_(u'Audit Content Type Life Cycle?'),
        description=_(
            u'Log content type life cycle events like object creation, modification and removal.'),  # noqa: E501
        default=True,
    )

    audit_workflow = schema.Bool(
        title=_(u'Audit Workflow Transitions?'),
        description=_(u'Log workflow transitions like object publishing.'),
        default=True,
    )

    audit_profile_imports = schema.Bool(
        title=_(u'Audit Profile Imports?'),
        description=_(
            u'Log Generic Setup profile imports; '
            u'this is useful to audit add-on installs/uninstalls.',
        ),
        default=True,
    )

    audit_registry = schema.Bool(
        title=_(u'Audit Registry?'),
        description=_(u'Log registry events like records being modified.'),
        default=True,
    )

    audit_iterate = schema.Bool(
        title=_(u'Audit Iterate?'),
        description=_(
            u'If plone.app.iterate is installed, '
            u'log events like content editing checkouts and checkins.'),
        default=True,
    )
