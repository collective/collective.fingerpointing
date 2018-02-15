# -*- coding: utf-8 -*-
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import all_audit_log_lines
from Products.Five.browser import BrowserView


DEFAULT_SIZE = 100


class LogView(BrowserView):

    @property
    def available(self):
        return log_info.has_log_file

    @property
    def page(self):
        try:
            return int(self.request.form.get('page', 1))
        except ValueError:
            return 1

    @property
    def size(self):
        try:
            return int(self.request.form.get('size', DEFAULT_SIZE))
        except ValueError:
            return DEFAULT_SIZE

    @property
    def query(self):
        return self.request.form.get('query', '').strip()

    def _filtered_audit_log_lines(self):
        """Generator for requested filtered log lines.
        """
        query = self.query
        for line in all_audit_log_lines():
            if not query or query in line:
                yield line

    def _batched_audit_log_lines(self):
        """Generator for requested batch of the already filtered log lines.
        """
        start = (self.page - 1) * self.size
        end = start + self.size
        for pos, line in enumerate(self._filtered_audit_log_lines()):
            if pos >= end:
                break
            if pos < start:
                continue
            yield line

    def build_audit_log(self):
        """Triggers build and sets attributes for use in template.
        """
        lines = [l for l in self._batched_audit_log_lines()]
        self.audit_log = '\n'.join(lines)
        self.has_next = len(lines) == self.size
        self.has_prev = self.page > 1

    @property
    def base_url(self):
        return self.context.absolute_url() + '/@@fingerpointing-audit-log'

    def pagination_url(self, type_, size=None):
        params = {'size': size if size is not None else self.size}
        if self.query:
            params['query'] = self.query
        if type_ == 'first':
            params['page'] = 1
        if type_ == 'prev':
            params['page'] = self.page - 1
        if type_ == 'next':
            params['page'] = self.page + 1
        return self.base_url + '?' + '&'.join(
            [k + '=' + str(v) for k, v in params.items()])
