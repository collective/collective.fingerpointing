.. image:: https://raw.githubusercontent.com/collective/collective.fingerpointing/master/docs/fingerpointing.png
    :align: left
    :alt: Finger Pointing
    :height: 100px
    :width: 100px

***************
Finger Pointing
***************

.. contents:: Table of Contents

Life, the Universe, and Everything
==================================

Keep track of different events and write them down to an audit log.

Mostly Harmless
===============

.. image:: http://img.shields.io/pypi/v/collective.fingerpointing.svg
   :target: https://pypi.python.org/pypi/collective.fingerpointing

.. image:: https://img.shields.io/travis/collective/collective.fingerpointing/master.svg
    :target: http://travis-ci.org/collective/collective.fingerpointing

.. image:: https://img.shields.io/coveralls/collective/collective.fingerpointing/master.svg
    :target: https://coveralls.io/r/collective/collective.fingerpointing

Got an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`opening a support ticket`: https://github.com/collective/collective.fingerpointing/issues

Known Issues
------------

Running your site behind a CDN may result in inconsistent IP addresses being logged.
In CloudFlare, for instance, you can work around this limitation by enabling a feature called ''True-Client-IP Header'',
but it requires an Enterprise plan.

Don't Panic
===========

Installation
------------

To enable this package in a buildout-based installation:

Edit your buildout.cfg and add the following to it:

.. code-block:: ini

    [buildout]
    ...
    eggs =
        collective.fingerpointing

By default, ``collective.fingerpointing`` logs audit events to the event log only.
   To enable logging to a separate file use the following configuration:

.. code-block:: ini

    [instance]
    zope-conf-additional +=
        <product-config collective.fingerpointing>
            audit-log ${buildout:directory}/var/log/audit.log
            audit-log-max-size 10240
            audit-log-old-files 30
        </product-config>

audit-log
    The filename of the audit log. Defaults to none.
audit-log-max-size
    Maximum size of audit log file. Enables log rotation.
audit-log-old-files
    Number of previous log files to retain when log rotation is enabled. Defaults to 1.

After updating the configuration you need to run ''bin/buildout'', which will take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``collective.fingerpointing`` and click the 'Activate' button.

Usage
-----

Go to 'Site Setup' and select 'Finger Pointing' and enable the events you want to keep an eye on.

.. figure:: https://raw.githubusercontent.com/collective/collective.fingerpointing/master/docs/controlpanel.png
    :align: center
    :height: 600px
    :width: 768px

    The Finger Pointing control panel configlet.

Finger Pointing will start logging the selected events:

.. code-block:: console

    # bin/instance fg
    2016-09-26 15:23:36 INFO ZServer HTTP server started at Mon Sep 26 15:23:36 2016
        Hostname: 0.0.0.0
        Port: 8080
    2016-09-26 15:23:41 INFO collective.fingerpointing Logging audit information to /home/hvelarde/collective/fingerpointing/var/log/audit.log
    2016-09-26 15:23:49 INFO Plone OpenID system packages not installed, OpenID support not available
    2016-09-26 15:23:56 INFO Zope Ready to handle requests
    2016-09-26 15:24:19 INFO collective.fingerpointing user=admin ip=127.0.0.1 action=logout
    2016-09-26 15:24:28 INFO collective.fingerpointing user=admin ip=127.0.0.1 action=login

These events are also logged in `var/log/audit.log`:

.. code-block:: console

    2016-09-26 15:24:19,717 - INFO - user=admin ip=127.0.0.1 action=logout
    2016-09-26 15:24:28,415 - INFO - user=admin ip=127.0.0.1 action=login

An audit log view is available in the user menu to users with the `collective.fingerpointing: View Audit Log` permission:

.. figure:: https://raw.githubusercontent.com/collective/collective.fingerpointing/master/docs/audit-log-view.png
    :align: left
    :alt: Finger Pointing
    :height: 480px
    :width: 768px

    The Finger Pointing audit log view.

If you specify no audit log file you'll see a warning;
however, audit events will be normally logged to the event log:

.. code-block:: console

    # bin/instance fg
    2016-09-26 15:58:32 INFO ZServer HTTP server started at Mon Sep 26 15:58:32 2016
        Hostname: 0.0.0.0
        Port: 8080
    2016-09-26 15:58:35 WARNING collective.fingerpointing No audit log file specified; audit log view will be disabled
    2016-09-26 15:58:40 INFO Plone OpenID system packages not installed, OpenID support not available
    2016-09-26 15:58:45 INFO Zope Ready to handle requests
    2016-09-26 15:58:48 INFO collective.fingerpointing user=admin ip=127.0.0.1 action=logout
    2016-09-26 15:58:54 INFO collective.fingerpointing user=admin ip=127.0.0.1 action=login
