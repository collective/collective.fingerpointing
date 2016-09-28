# -*- coding: utf-8 -*-
from App.config import getConfiguration


PROJECTNAME = 'collective.fingerpointing'
AUDIT_MESSAGE = u'user={0} ip={1} action={2} {3}'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# read configuration from zope.conf
zopeConf = getConfiguration()
product_config = getattr(zopeConf, 'product_config', {})
fingerpointing_config = product_config.get(PROJECTNAME, {})
