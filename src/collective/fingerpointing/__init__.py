from zope.i18nmessageid import MessageFactory


_ = MessageFactory('collective.fingerpointing')


# fire events for role changes; Plone does not notify these itself
from collective.fingerpointing import patches  # noqa: E402


patches.apply()
