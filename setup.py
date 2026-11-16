from setuptools import setup

version = "2.0.0.dev0"
description = "Keep track of different events and write them down to an audit log."
long_description = (
    open("README.rst").read()
    + "\n"
    + open("CONTRIBUTORS.rst").read()
    + "\n"
    + open("CHANGES.rst").read()
)

setup(
    name="collective.fingerpointing",
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "Framework :: Plone",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    keywords="plone events subscribers log audit security",
    author="Hector Velarde",
    author_email="hector.velarde@gmail.com",
    url="https://github.com/collective/collective.fingerpointing",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "file_read_backwards",
        "plone.api >=1.5.1",
        "plone.app.registry",
        "plone.registry",
        "Products.CMFCore",
        "plone.base",
        "Products.CMFPlone",
        "Products.GenericSetup",
        "Products.PluggableAuthService >=1.11.0",
        "zc.lockfile>=1.2.1",
        "zope.globalrequest",
        "zope.i18nmessageid",
        "zope.interface",
        "zope.lifecycleevent",
        "zope.schema",
        "Zope",
    ],
    extras_require={
        "test": [
            "AccessControl",
            "plone.app.contenttypes",
            "plone.app.iterate",
            "plone.app.robotframework",
            "plone.app.testing",
            "plone.browserlayer",
            "plone.testing",
            "Products.PlonePAS",
            "robotsuite",
            "testfixtures",
            "zope.component",
            "zope.event",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
