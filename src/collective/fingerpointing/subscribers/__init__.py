from .genericsetup_logger import profile_imports_logger  # noqa: F401
from .lifecycle_logger import lifecycle_logger  # noqa: F401
from .pas_logger import failed_api_login_logger  # noqa: F401
from .pas_logger import failed_login_logger  # noqa: F401
from .pas_logger import pas_logger  # noqa: F401
from .registry_logger import registry_logger  # noqa: F401
from .roles_logger import roles_logger  # noqa: F401
from .workflow_logger import workflow_logger  # noqa: F401

import importlib.util


# plone.app.iterate is dependency of the "Plone" package, but not of
# the Products.CMFPlone. So dependend on the way Plone is installed it
# might be not available.
if importlib.util.find_spec('plone.app.iterate') is not None:
    from .iterate_logger import iterate_logger  # noqa: F401
