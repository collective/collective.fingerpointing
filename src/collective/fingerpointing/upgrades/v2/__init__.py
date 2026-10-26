from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.logger import commonlogger


def update_configlet(setup_tool):
    """Update control panel configlet."""
    profile = f'profile-{PROJECTNAME}:default'
    setup_tool.runImportStepFromProfile(profile, 'controlpanel')
    commonlogger.info('Control panel configlet updated.')


def update_user_actions(setup_tool):
    """Update user actions."""
    profile = f'profile-{PROJECTNAME}:default'
    setup_tool.runImportStepFromProfile(profile, 'rolemap')
    commonlogger.info('Permissions updated.')
    setup_tool.runImportStepFromProfile(profile, 'actions')
    commonlogger.info('User actions updated.')
