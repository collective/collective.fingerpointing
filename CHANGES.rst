Changelog
=========

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
