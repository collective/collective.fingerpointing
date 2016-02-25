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
            u'Log authentication events like users logging in and loggin out.'),
        default=True,
    )

    audit_lifecycle = schema.Bool(
        title=_(u'Audit Content Type Life Cycle?'),
        description=_(
            u'Log content type life cycle events like object creation, modification and removal.'),
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
            u'log events like content editing checkouts and checkins.'
        ),
        default=True,
    )
