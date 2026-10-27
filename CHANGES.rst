Changelog
=========

2.0.0a1 (unreleased)
--------------------

Breaking changes:

- Support Plone 6.0, 6.1 and 6.2 on Python 3.11 – 3.14 only.
  Use 1.8.x for Plone 4.3 – 6.0 on Python 2.7 or 3.6 – 3.9.
  Removed Archetypes support and the Plone 4.3 ``Extensions/Install.py``.
  [jladage]

- Use a native (PEP 420) namespace package: ``pkg_resources`` is gone from setuptools 81, which Plone 6.1 and 6.2 use.
  [jladage]

- Newlines in logged values are escaped in the text format, so user input like a login name cannot forge audit log lines.
  This changes how multi-line registry values are logged.
  [jladage]

New features:

- Position Finger Pointing as NIS2 audit logging for Plone, to be combined with log monitoring tools like SigNoz.
  [jladage]

- Add ``audit-log-handler`` setting to write audit events to a file (the default), to syslog over UDP or TCP, or to standard output for container log collectors.
  [jladage]

- Add ``audit-log-format`` setting: ``text`` (the default, as before) or ``json``, one object per line with the details of the event.
  [jladage]

- All settings can also be set with ``FINGERPOINTING_*`` environment variables, which override ``zope.conf``.
  [jladage]

- Log failed logins, through the Classic UI login form and the ``@login`` REST API endpoint used by Volto, with level ``WARNING``.
  [jladage]

- Log group creation, group membership changes, password changes and changes to user properties.
  Only the names of changed properties are logged, never passwords or property values.
  [jladage]

- Add "Audit Role Assignments" setting (upgrade step to profile version 6), to log changes to global roles of users and groups, to local roles through the sharing view and the ``@sharing`` REST API endpoint, and to local role inheritance.
  Plone fires no events for global role changes, and its event for local role changes does not tell what has changed, so Finger Pointing patches the PlonePAS role manager and the sharing view to fire ``IPrincipalRolesModifiedEvent``, ``ILocalRolesModifiedEvent`` and ``ILocalRolesInheritanceModifiedEvent``.
  With Products.PluggableAuthService 4.3 or later, use its ``IRoleAssignedToPrincipalEvent`` and ``IRoleRemovedFromPrincipalEvent`` instead of patching ``assignRoleToPrincipal`` and ``removeRoleFromPrincipal``.
  With older versions, log a warning at startup to pin Products.PluggableAuthService to 4.3 or newer.
  [jladage]

- Add ``log_info.audit(user, ip, action, details)`` to log audit events with structured details from other packages.
  Calling ``log_info(message)`` still works.
  [jladage]

Bug fixes:

- Fix tests on Plone 6.1+: the profile of plone.app.iterate is now called ``default``, and plone.app.discussion is no longer part of Plone.
  [jladage]

- Write the audit log file as UTF-8, whatever the locale.
  [jladage]

- Remove the old handler when the logger is reconfigured without an audit log file.
  [jladage]

- Do not fail when an event is fired outside a request or a Plone site, like in scripts.
  [jladage]

Internal:

- Test with tox against the constraints of each Plone release, instead of buildout.
  [jladage]


1.8.3 (2022-05-06)
------------------

- Setup CI: test in 4.3, 5.1, 5.2, 6.0.  [maurits]

- Fix ImportError in Plone 6.  [maurits]


1.8.2 (2020-03-16)
------------------

- Fix typo in French translation.
  [laulaz]

- In ``workflow_logger`` display full path of object instead just object id.
  [gbastien]


1.8.1 (2019-11-22)
------------------

- Do not fail running ``plone-compile-resources`` together with fingerpointing installed in Plone 5.2.
  [jensens]

- Completed french translations.
  [gbastien]


1.8 (2018-10-11)
----------------

- Avoid ``TypeError`` when View Audit Log (fixes `#91 <https://github.com/collective/collective.fingerpointing/issues/91>`_).
  [jianaijun]

- Update Chinese Simplified translation.
  [jianaijun]


1.7 (2018-04-23)
----------------

- Drop support for Plone 5.0.
  [hvelarde]

- Avoid ``ComponentLookupError`` when adding a Plone site (fixes `#85 <https://github.com/collective/collective.fingerpointing/issues/85>`_).
  [hvelarde]

- Do not fail while logging uninstall profile information.
  [hvelarde]

- Fix uninstall of control panel configlet under Plone 5.1.
  [hvelarde]


1.6 (2018-03-28)
----------------

- Avoid ``TypeError`` on PAS events (fixes `#78 <https://github.com/collective/collective.fingerpointing/issues/78>`_).
  [hvelarde]


1.6rc2 (2018-03-22)
-------------------

- Fix profile version number.
  [hvelarde]


1.6rc1 (2018-03-22)
-------------------

- Update i18n, Brazilian Portuguese and Spanish translations.
  [hvelarde]

- Code clean up and refactor, avoid ``UnicodeEncodeError`` on registry subscriber (refs. `#74 <https://github.com/collective/collective.fingerpointing/issues/74>`_).
  [hvelarde]

- Log Generic Setup profile imports; this is useful to audit add-on installs/uninstalls (implements `#32 <https://github.com/collective/collective.fingerpointing/issues/32>`_).
  [hvelarde]

- Do label `Size` translatable, completed french translations.
  [gbastien]


1.5rc1 (2017-11-24)
-------------------

- Update i18n, Brazilian Portuguese, German and Spanish translations.
  [hvelarde, jensens]

- Lock-file is now container save and it's close more robust.
  [jensens]

- Refactor logger module in order to improve testability.
  [jensens]

- Add search on audit logs and pagination (implements `#17 <https://github.com/collective/collective.fingerpointing/issues/17>`_).
  [jensens]


1.4b3 (2017-11-21)
------------------

- Fix object location for lifecycle logger by subscribing to ``IObjectAddedEvent`` (fixes `#66 <https://github.com/collective/collective.fingerpointing/issues/66>`_).
  [jensens]

- Do not fail on startup if plone.app.iterate is not installed (fixes `#64 <https://github.com/collective/collective.fingerpointing/issues/64>`_).
  [jensens]

- Reviewed and updated German translations.
  [jensens]


1.4b2 (2017-09-20)
------------------

- Add French translations.
  [gbastien]


1.4b1 (2017-06-26)
------------------

- Fix `AttributeError` when logging activity from anonymous users (fixes `#57 <https://github.com/collective/collective.fingerpointing/issues/57>`_).
  [keul]

- Add support for ``HTTP_X_FORWARDED_FOR`` request header to log real client IP addresses.
  [keul]


1.3b2 (2017-05-25)
------------------

- Avoid possible ``ConfigurationConflictError`` on upgrade step registration.
  [hvelarde]


1.3b1 (2017-05-25)
------------------

- Add support for Cloudflare's ``CF-Connecting-IP`` request header to log real client IP addresses.
  [hvelarde]

- We now use plone.api to get the id of the user instead of the ``AUTHENTICATED_USER`` key on the request.
  Also, we now use the ``getClientAddr()`` function to get remote IP address.
  These changes simplify testing.

- Add support for logging workflow transitions.
  [hvelarde]

- Avoid ComponentLookupError when plonectl adduser.
  [jianaijun]


1.2b1 (2016-09-28)
------------------

.. Warning::
    Starting with this version you need to explicitly configure the package to use a separate audit.log file.
    Check the documentation to find out how to do so.

- Make log rotating configurable using the `zope-conf-additional` option.
  Note that now, by default, rotating is disabled.
  [rene, hvelarde]


1.1b1 (2016-07-07)
------------------

- Drop support for Plone 4.2.
  [hvelarde]

- Log deletion of groups too.
  If you are using Plone < 4.3.8 you may need to update versions of `Products.PlonePAS` and `Products.PluggableAuthService`.
  [fRiSi]


1.0b4 (2016-07-07)
------------------

- Avoid UnicodeEncodeError with log messages.
  [jianaijun, rodfersou]

- Support automatic rotation of audit log files at timed intervals;
  a new file is created every day and up to 30 backup files are maintained (closes `#9`_).
  [hvelarde]

- Use object representation to log life cycle events;
  this fixes an issue with Archetypes-based objects being dumped to the log (refs. `#8`_ and fixes `#38`_).
  [hvelarde]

- Package is now compatible with Plone 5.0 and Plone 5.1.
  [hvelarde]


1.0b3 (2016-04-19)
------------------

- Added Chinese Simplified translation. [jianaijun]

- Package no longer rises `AttributeError` when running interactive console (`bin/instance debug`) (fixes `#30`_).
  [hvelarde]

- Clean up audit log messages.
  [hvelarde]

- Disable rendering of left and right columns in audit log view.
  [hvelarde]

- Audit log entries are now shown in reverse order (newer entries first).
  [hvelarde]


1.0b2 (2016-03-18)
------------------

- Log to audit.log even if Zope's `event-log-level` is above INFO (fixes `#25`_).
  [fRiSi]

- Add German translations.
  [fRiSi]

- Fix output of the audit log view.
  [pcdummy, hvelarde]

- Add Brazilian Portuguese and Spanish translations.
  [hvelarde]

- The "View Audit log" action appears now before the "Log out" one (fixes `#18`_).
  [pcdummy, hvelarde]

- Use main_template for the audit log view.
  [pcdummy]

- Avoid `TypeError` while running third party tests (fixes `#2`_).
  [hvelarde]


1.0b1 (2016-03-09)
------------------

- Add a view for the audit.log file `@@fingerpointing-audit-log` and link it to portal_actions.
  [pcdummy, hvelarde]

- Make control panel configlet accesible to Site Administrator role (closes `#15`_).
  [hvelarde]

- Avoid ``ComponentLookupError`` when removing a Plone site (fixes `#4`_).
  [hvelarde]

- Remove unused plone.directives.form dependency which pulled in Grok packages.
  [vangheem]

- Audit information is now logged into a file named `audit.log` instead of inside the standard `event.log`.
  [pcdummy]

- Package is now compatible with Plone 5.
  [hvelarde]

- Ignore errors caused by subscribers trying to access nonexistent registry records when package is still not installed (fixes `#1`_).
  [hvelarde]


1.0a1 (2015-06-08)
------------------

- Initial release.

.. _`#1`: https://github.com/collective/collective.fingerpointing/issues/1
.. _`#2`: https://github.com/collective/collective.fingerpointing/issues/2
.. _`#4`: https://github.com/collective/collective.fingerpointing/issues/4
.. _`#8`: https://github.com/collective/collective.fingerpointing/issues/8
.. _`#9`: https://github.com/collective/collective.fingerpointing/issues/9
.. _`#15`: https://github.com/collective/collective.fingerpointing/issues/15
.. _`#18`: https://github.com/collective/collective.fingerpointing/issues/18
.. _`#25`: https://github.com/collective/collective.fingerpointing/issues/25
.. _`#30`: https://github.com/collective/collective.fingerpointing/issues/30
.. _`#38`: https://github.com/collective/collective.fingerpointing/issues/38
