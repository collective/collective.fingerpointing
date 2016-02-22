Changelog
=========

1.0a2 (unreleased)
------------------

- Audit information is now logged into a file named `audit.log` instead of inside the standard `event.log`.
  [jochum]

- Ignore errors caused by subscribers trying to access nonexistent registry records when package is still not installed (fixes `#1`_).
  [hvelarde]

1.0a1 (2015-06-08)
------------------

- Initial release.

.. _`#1`: https://github.com/collective/collective.fingerpointing/issues/1
