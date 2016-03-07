# -*- coding: utf-8 -*-
from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.logger import logger


def update_configlet(setup_tool):
    """Update control panel configlet."""
    profile = 'profile-{0}:default'.format(PROJECTNAME)
    setup_tool.runImportStepFromProfile(profile, 'controlpanel')
    logger.info('Control panel configlet updated.')


def update_user_actions(setup_tool):
    """Update user actions."""
    profile = 'profile-{0}:default'.format(PROJECTNAME)
    setup_tool.runImportStepFromProfile(profile, 'rolemap')
    logger.info('Permissions updated.')
    setup_tool.runImportStepFromProfile(profile, 'actions')
    logger.info('User actions updated.')
