from App.config import getConfiguration

import os


PROJECTNAME = 'collective.fingerpointing'
AUDIT_MESSAGE = 'user={0} ip={1} action={2} {3}'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Settings read from the product-config section in zope.conf.
CONFIG_KEYS = (
    'audit-log',
    'audit-log-max-size',
    'audit-log-old-files',
    'audit-log-handler',
    'audit-log-format',
    'audit-syslog-address',
    'audit-syslog-socktype',
    'audit-syslog-facility',
)


def environment_variable(key):
    """Return the environment variable that overrides a setting,
    e.g. FINGERPOINTING_AUDIT_LOG_HANDLER for audit-log-handler.
    """
    return 'FINGERPOINTING_' + key.upper().replace('-', '_')


def read_config(product_config, environ):
    config = dict(product_config.get(PROJECTNAME) or {})
    for key in CONFIG_KEYS:
        value = environ.get(environment_variable(key))
        if value:
            config[key] = value
    return config


# read configuration from zope.conf and the environment
zopeConf = getConfiguration()
product_config = getattr(zopeConf, 'product_config', None) or {}
fingerpointing_config = read_config(product_config, os.environ)
