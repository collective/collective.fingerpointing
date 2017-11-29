# -*- coding: utf-8 -*-
from .genericsetup_logger import profile_imports_logger  # noqa: F401
from .lifecycle_logger import lifecycle_logger  # noqa: F401
from .pas_logger import pas_logger  # noqa: F401
from .registry_logger import registry_logger  # noqa: F401
from .workflow_logger import workflow_logger  # noqa: F401

import pkg_resources


try:
    # plone.app.iterate is dependency of the "Plone" package, but not of
    # the Products.CMFPlone. So dependend on the way Plone is installed it
    # might be not available.
    pkg_resources.get_distribution('plone.app.iterate')
except pkg_resources.DistributionNotFound:
    pass
else:
    from .iterate_logger import iterate_logger  # noqa: F401
