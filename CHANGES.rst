Changelog
=========

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

- Avoid `ComponentLookupError` when removing a Plone site (fixes `#4`_).
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
.. _`#15`: https://github.com/collective/collective.fingerpointing/issues/15
.. _`#18`: https://github.com/collective/collective.fingerpointing/issues/18
.. _`#25`: https://github.com/collective/collective.fingerpointing/issues/25
