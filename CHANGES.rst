Changelog
=========

1.0b1 (2016-03-09)
------------------

- Add a view for the audit.log file `@@fingerpointing-log` and link it to portal_actions.
  [pcdummy, hvelarde]

- Make control panel configlet accesible to Site Administrator role (closes `#18`_).
  [hvelarde]

- Avoid `ComponentLookupError` when removing a Plone site (fixes `#2`_).
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
.. _`#18`: https://github.com/collective/collective.fingerpointing/issues/18
