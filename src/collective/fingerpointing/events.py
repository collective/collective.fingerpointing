from collective.fingerpointing.interfaces import ILocalRolesInheritanceModifiedEvent  # noqa: E501
from collective.fingerpointing.interfaces import ILocalRolesModifiedEvent
from collective.fingerpointing.interfaces import IPrincipalRolesModifiedEvent
from zope.interface import implementer
from zope.interface.interfaces import ObjectEvent


@implementer(IPrincipalRolesModifiedEvent)
class PrincipalRolesModifiedEvent:

    def __init__(self, principal_id, old_roles, new_roles):
        self.principal_id = principal_id
        self.old_roles = tuple(old_roles)
        self.new_roles = tuple(new_roles)


@implementer(ILocalRolesModifiedEvent)
class LocalRolesModifiedEvent(ObjectEvent):

    def __init__(self, object, principal_id, old_roles, new_roles):
        super().__init__(object)
        self.principal_id = principal_id
        self.old_roles = tuple(old_roles)
        self.new_roles = tuple(new_roles)


@implementer(ILocalRolesInheritanceModifiedEvent)
class LocalRolesInheritanceModifiedEvent(ObjectEvent):

    def __init__(self, object, inherit):
        super().__init__(object)
        self.inherit = inherit
