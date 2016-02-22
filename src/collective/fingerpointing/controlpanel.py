# -*- coding: utf-8 -*-
from collective.fingerpointing import _
from collective.fingerpointing.interfaces import IFingerPointingSettings
from plone.app.registry.browser import controlpanel


class FingerPointingSettingsEditForm(controlpanel.RegistryEditForm):

    """Control panel edit form."""

    schema = IFingerPointingSettings
    label = _(u'Finger Pointing')
    description = _(u'Settings for the collective.fingerpointing package')


class FingerPointingSettingsControlPanel(controlpanel.ControlPanelFormWrapper):

    """Control panel form wrapper."""

    form = FingerPointingSettingsEditForm
