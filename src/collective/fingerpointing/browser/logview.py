# -*- coding: utf-8 -*-
from App.config import getConfiguration
from collective.fingerpointing import _
from collective.fingerpointing.config import AUDITLOG
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import os
import os.path


def tail(f, lines=20):
    """ From:
    http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    """

    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, os.SEEK_END)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []  # blocks of size BLOCK_SIZE, in reverse order starting
    # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0, os.SEEK_SET)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])


# by default, the audit log will use the same location used for the event log
eventlog = getattr(getConfiguration(), 'eventlog', None)

# on tests, eventlog is not set; we need to handle that
if eventlog is not None:
    logpath = eventlog.handler_factories[0].instance.baseFilename
    logfolder = os.path.split(logpath)[0]
    logfile = os.path.join(logfolder, AUDITLOG)
else:
    logfile = AUDITLOG


class LogView(BrowserView):
    index = ViewPageTemplateFile('logview.pt')

    def __call__(self):

        self.show_all = False
        if 'show_all' in self.request.form:
            self.show_all = True

        return self.render()

    def render(self):
        return self.index()

    def label(self):
        return _("Fingerpointing log view")

    @property
    def logcontents(self):
        with open(logfile, 'r') as fp:
            if not self.show_all:
                return tail(fp, 100)
            else:
                return fp.read()
