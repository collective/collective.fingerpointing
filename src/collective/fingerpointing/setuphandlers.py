from plone.base.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:

    def getNonInstallableProfiles(self):
        """Return a list of non-installable profiles."""
        return [
            'collective.fingerpointing:uninstall',
        ]
