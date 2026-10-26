"""Setup testing infrastructure."""
from collective.fingerpointing.config import PROJECTNAME
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.base.utils import get_installer

import importlib.util
import os
import shutil
import tempfile


HAS_ITERATE = importlib.util.find_spec('plone.app.iterate') is not None


class UninstallMixin:

    def uninstall(self):
        qi = get_installer(self.portal, self.request)
        with api.env.adopt_roles(['Manager']):
            qi.uninstall_product(PROJECTNAME)
        return qi


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

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

        import plone.restapi
        self.loadZCML(package=plone.restapi)

        import collective.fingerpointing
        self.loadZCML(package=collective.fingerpointing)

    def setUpPloneSite(self, portal):
        if HAS_ITERATE:
            self.applyProfile(portal, 'plone.app.iterate:default')

        self.applyProfile(portal, 'plone.restapi:default')
        self.applyProfile(portal, 'collective.fingerpointing:default')
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')

    def tearDown(self):
        super().tearDown()
        self._cleanup_audit_log()


FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name='collective.fingerpointing:Integration')

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name='collective.fingerpointing:Functional')
