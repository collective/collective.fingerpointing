# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '1.1b1'
description = 'Keep track of different events and write them down to an audit log.'
long_description = (
    open('README.rst').read() + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(
    name='collective.fingerpointing',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.0',
        # 'Framework :: Plone :: 5.1',
        'Framework :: Plone',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
    ],
    keywords='plone events subscribers log audit security',
    author='Hector Velarde',
    author_email='hector.velarde@gmail.com',
    url='https://github.com/collective/collective.fingerpointing',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'plone.app.registry',
        'plone.registry',
        'Products.CMFCore',
        'Products.CMFPlone >=4.3',
        'Products.GenericSetup',
        'Products.PlonePAS >=5.0.9',
        'Products.PluggableAuthService >=1.11.0',
        'setuptools',
        'zc.lockfile',
        'zope.component',
        'zope.globalrequest',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
    ],
    extras_require={
        'test': [
            'AccessControl',
            'plone.app.dexterity',
            'plone.app.iterate',
            'plone.app.robotframework',
            'plone.app.testing [robot]',
            'plone.browserlayer',
            'plone.testing',
            'robotsuite',
            'testfixtures',
            'zope.component',
            'zope.event',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
