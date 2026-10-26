from collective.fingerpointing.config import PROJECTNAME
from collective.fingerpointing.logger import commonlogger


def update_user_actions(setup_tool):
    """Update user actions."""
    profile = f'profile-{PROJECTNAME}:default'
    setup_tool.runImportStepFromProfile(profile, 'actions')
    commonlogger.info('User actions updated.')
