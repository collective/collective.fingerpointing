# -*- coding: utf-8 -*-
from collective.fingerpointing.logger import logfile
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
    def get_audit_log(self):
        """Return audit log with newer entries first."""
        with open(logfile, 'r') as fp:
            lines = self.tail(fp)

        lines.reverse()
        return ''.join(lines)
