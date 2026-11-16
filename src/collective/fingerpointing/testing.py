# -*- coding: utf-8 -*-
"""Setup testing infrastructure.

For Plone 5 we need to install plone.app.contenttypes.
"""
from collective.fingerpointing.config import PROJECTNAME
from plone import api
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from zope.globalrequest import setRequest

import os
import pkg_resources
import shutil
import tempfile


try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    from plone.app.testing import PLONE_FIXTURE
else:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE as PLONE_FIXTURE  # noqa: E501

try:
    pkg_resources.get_distribution('plone.app.iterate')
except pkg_resources.DistributionNotFound:
    HAS_ITERATE = False
else:
    HAS_ITERATE = True

plone_version = float(api.env.plone_version()[:3])

if plone_version >= 5.2:
    from plone.testing.zope import WSGI_SERVER_FIXTURE as SERVER_FIXTURE
else:
    from plone.testing.z2 import ZSERVER_FIXTURE as SERVER_FIXTURE

MANAGER_NAME = 'manager'
MANAGER_PASSWORD = 'manager123'
MEMBER_NAME = 'member'
MEMBER_PASSWORD = 'member123'
IS_PLONE_6 = plone_version >= 6.0
IS_PLONE_5 = plone_version >= 5.1
IS_BBB = plone_version < 5.0


class QIBBB:
    """BBB: remove on deprecation of Plone 4.3."""
    def uninstall(self):
        if IS_BBB:
            qi = self.portal['portal_quickinstaller']
            with api.env.adopt_roles(['Manager']):
                qi.uninstallProducts([PROJECTNAME])
        else:
            from plone.base.utils import get_installer
            qi = get_installer(self.portal, self.request)
            with api.env.adopt_roles(['Manager']):
                qi.uninstall_product(PROJECTNAME)
        return qi


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    # XXX: this can probably be done in a different way
    def _setup_audit_log(self):
        """Fake configuration for collective.fingerpointing as tests
        expect an audit.log file to be set.
        """
        from collective.fingerpointing.config import fingerpointing_config
        from collective.fingerpointing.logger import log_info
        self.temp_dir = tempfile.mkdtemp()
        fingerpointing_config['audit-log'] = os.path.join(
            self.temp_dir,
            'audit.log',
        )
        log_info.configure(fingerpointing_config)

    def _cleanup_audit_log(self):
        from collective.fingerpointing.config import fingerpointing_config
        fingerpointing_config['audit-log'] = None
        shutil.rmtree(self.temp_dir)

    def setUpZope(self, app, configurationContext):
        self._setup_audit_log()
        if HAS_ITERATE:
            import plone.app.iterate
            self.loadZCML(package=plone.app.iterate)

        import collective.fingerpointing
        self.loadZCML(package=collective.fingerpointing)

    def setUpPloneSite(self, portal):
        if HAS_ITERATE:
            self.applyProfile(portal, 'plone.app.iterate:plone.app.iterate')

        self.applyProfile(portal, 'collective.fingerpointing:default')
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        # robot users: a Manager and a plain Member; the PAS subscriber
        # reads the global request
        setRequest(portal.REQUEST)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        api.user.create(
            email='manager@example.com', username=MANAGER_NAME,
            password=MANAGER_PASSWORD, roles=('Member', 'Manager'))
        api.user.create(
            email='member@example.com', username=MEMBER_NAME,
            password=MEMBER_PASSWORD)
        setRoles(portal, TEST_USER_ID, ['Member'])
        logout()
        setRequest(None)

    def tearDown(self):
        super(Fixture, self).tearDown()
        self._cleanup_audit_log()


FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name='collective.fingerpointing:Integration')

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name='collective.fingerpointing:Functional')

ACCEPTANCE = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, SERVER_FIXTURE),
    name='collective.fingerpointing:Acceptance')
