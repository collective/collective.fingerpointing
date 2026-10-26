from setuptools import find_namespace_packages
from setuptools import setup


version = '2.0.0a1'
description = (
    'NIS2 audit logging for Plone: record security-relevant events '
    'for log monitoring tools like SigNoz.'
)
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
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Plone :: 6.0',
        'Framework :: Plone :: 6.1',
        'Framework :: Plone :: 6.2',
        'Framework :: Plone :: Addon',
        'Framework :: Plone',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: System :: Logging',
    ],
    keywords='plone events subscribers log audit security nis2 syslog',
    author='Hector Velarde',
    author_email='hector.velarde@gmail.com',
    url='https://github.com/collective/collective.fingerpointing',
    license='GPLv2',
    packages=find_namespace_packages('src', include=['collective.*']),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.10',
    install_requires=[
        'file_read_backwards',
        'plone.api >=2.0',
        'plone.app.registry',
        'plone.app.workflow',
        'plone.base',
        'plone.registry',
        'Products.CMFCore',
        'Products.CMFPlone >=6.0',
        'Products.GenericSetup',
        'Products.PlonePAS',
        'Products.PluggableAuthService',
        'zc.lockfile>=1.2.1',
        'zope.component',
        'zope.globalrequest',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
        'Zope',
    ],
    extras_require={
        'test': [
            'plone.app.contenttypes[test]',
            'plone.app.iterate',
            'plone.app.testing',
            'plone.browserlayer',
            'plone.restapi',
            'plone.testing',
            'testfixtures',
            'zope.testrunner',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
