# -*- coding: utf-8 -*-
from collective.fingerpointing.logger import logfile as LOGFILE
from glob import glob
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class LogView(BrowserView):

    index = ViewPageTemplateFile('logview.pt')

    def __call__(self):
        return self.render()

    def render(self):
        return self.index()

    def tail(self, f, n=100):
        """Return the last n lines of a file.
        See: http://stackoverflow.com/a/280083/644075
        """
        assert n >= 0
        pos, lines = n + 1, []
        while len(lines) <= n:
            try:
                f.seek(-pos, 2)
            except IOError:
                f.seek(0)
                break
            finally:
                lines = list(f)
            pos *= 2
        return lines[-n:]

    @property
    def _get_audit_log_files(self):
        """Return a list with the current audit log and all of its
        backups. The list is sorted with newer files first.
        """
        # retrieve the list of audit log backup files
        logfiles = sorted([
            f for f in glob(LOGFILE + '.*') if '.lock' not in f
        ], reverse=True)
        # include active audit log as first element
        logfiles.insert(0, LOGFILE)
        return logfiles

    @property
    def get_audit_log(self):
        """Return audit log with newer entries first."""
        lines = []
        # process all logs until we have enough lines
        for logfile in self._get_audit_log_files:
            with open(logfile, 'r') as fp:
                lines.extend(self.tail(fp))
            if len(lines) >= 100:
                break

        lines = sorted(lines[:100], reverse=True)
        return ''.join(lines)
