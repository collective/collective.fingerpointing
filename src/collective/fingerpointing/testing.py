# -*- coding: utf-8 -*-
"""Setup testing infrastructure."""
from collective.fingerpointing import get_version
from collective.fingerpointing import PackageNotFoundError
from collective.fingerpointing.config import PROJECTNAME
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.base.utils import get_installer
from plone.testing.zope import WSGI_SERVER_FIXTURE
from zope.globalrequest import setRequest

import os
import shutil
import tempfile


try:
    get_version("plone.app.iterate")
except PackageNotFoundError:
    HAS_ITERATE = False
else:
    HAS_ITERATE = True

MANAGER_NAME = "manager"
MANAGER_PASSWORD = "manager123"
MEMBER_NAME = "member"
MEMBER_PASSWORD = "member123"


class UninstallMixin:
    def uninstall(self):
        qi = get_installer(self.portal, self.request)
        with api.env.adopt_roles(["Manager"]):
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
        fingerpointing_config["audit-log"] = os.path.join(
            self.temp_dir,
            "audit.log",
        )
        log_info.configure(fingerpointing_config)

    def _cleanup_audit_log(self):
        from collective.fingerpointing.config import fingerpointing_config

        fingerpointing_config["audit-log"] = None
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
            self.applyProfile(portal, "plone.app.iterate:default")

        self.applyProfile(portal, "collective.fingerpointing:default")
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        # robot users: a Manager and a plain Member; the PAS subscriber
        # reads the global request
        setRequest(portal.REQUEST)
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        api.user.create(
            email="manager@example.com",
            username=MANAGER_NAME,
            password=MANAGER_PASSWORD,
            roles=("Member", "Manager"),
        )
        api.user.create(
            email="member@example.com", username=MEMBER_NAME, password=MEMBER_PASSWORD
        )
        setRoles(portal, TEST_USER_ID, ["Member"])
        logout()
        setRequest(None)

    def tearDown(self):
        super(Fixture, self).tearDown()
        self._cleanup_audit_log()


FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="collective.fingerpointing:Integration"
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="collective.fingerpointing:Functional"
)

ACCEPTANCE = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, WSGI_SERVER_FIXTURE),
    name="collective.fingerpointing:Acceptance",
)
