# coding=utf-8
# Furitsuki Anki Plugin
# Copyright (C) 2016  Stephen McIntosh <stephenmac7@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#from __future__ import print_function
from anki.hooks import addHook
from aqt import QProcess, QAction, mw

CONFIG = {
    'srcFields': ['Expression'],
    'dstFields': ['Reading'],
    # For bulk readings, filter models
    'checkModel': False,
    'models': [],
    # Automatically add reading when focus lost on an srcField
    # Conflicts with the Japanese Support plugin
    'addOnFocusLost': True
}

JAR_FILE = '../../addons/furitsuki/furitsuki.jar'
PROC_CMD = 'java'
PROC_ARGS = ['-jar', JAR_FILE]

class FuritsukiController:
    def __init__(self):
        self.proc = None

    def ensure_open(self, warmup = True):
        if not self.proc or self.proc.state() == QProcess.NotRunning:
            self.proc = QProcess(mw)
            self.proc.start(PROC_CMD, PROC_ARGS)
            self.proc.waitForStarted()
            if warmup:
                self.proc.write('私\n') # Get things running, as it takes a while to load the dictionaries
                self.proc.readyReadStandardOutput.connect(self.warmup_ready)

    def warmup_ready(self):
        self.proc.readAllStandardOutput() # Eat the output from the warmup
        self.proc.readyReadStandardOutput.disconnect(self.warmup_ready)

    def write_input(self, text):
        self.proc.write(text.replace('\n', ' ').encode('utf-8')) # Make sure we only have one line
        self.proc.write(u'\n')
        self.proc.waitForBytesWritten()

    def reading(self, text):
        self.ensure_open(warmup = False)
        self.write_input(text)
        self.proc.waitForReadyRead()
        return unicode(str(self.proc.readLine()), 'utf-8')

# Shamelessly copied from the Japanese Support plugin -- but this is GPL so it's all good
def onFocusLost(flag, n, fidx):
    global furitsuki
    if not furitsuki:
        return flag
    src = None
    dst = None
    # have src and dst fields?
    for c, name in enumerate(mw.col.models.fieldNames(n.model())):
        for f in CONFIG['srcFields']:
            if name == f:
                src = f
                srcIdx = c
        for f in CONFIG['dstFields']:
            if name == f:
                dst = f
    if not src or not dst:
        return flag
    # dst field already filled?
    if n[dst]:
        return flag
    # event coming from src field?
    if fidx != srcIdx:
        return flag
    # grab source text
    srcTxt = mw.col.media.strip(n[src])
    if not srcTxt:
        return flag
    # update field
    try:
        n[dst] = furitsuki.reading(srcTxt)
    except Exception, e:
        furitsuki = None
        raise
    return True

def regenerateReadings(nids):
    global furitsuki
    mw.checkpoint("Bulk-add Readings")
    mw.progress.start()
    for nid in nids:
        note = mw.col.getNote(nid)
        if CONFIG['checkModel'] and note.model()['name'].lower() not in CONFIG['models']:
            continue
        src = None
        for fld in CONFIG['srcFields']:
            if fld in note:
                src = fld
                break
        if not src:
            # no src field
            continue
        dst = None
        for fld in CONFIG['dstFields']:
            if fld in note:
                dst = fld
                break
        if not dst:
            # no dst field
            continue
        if note[dst]:
            # already contains data, skip
            continue
        srcTxt = mw.col.media.strip(note[src])
        if not srcTxt.strip():
            continue
        try:
            note[dst] = furitsuki.reading(srcTxt)
        except Exception, e:
            mecab = None
            raise
        note.flush()
    mw.progress.finish()
    mw.reset()

def setupMenu(browser):
    a = QAction("Furitsuki Bulk-add Readings", browser)
    a.triggered.connect(lambda x: onRegenerate(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

def onRegenerate(browser):
    regenerateReadings(browser.selectedNotes())

# Init
furitsuki = FuritsukiController()
if CONFIG['addOnFocusLost']:
    addHook('editFocusLost', onFocusLost)
addHook('profileLoaded', furitsuki.ensure_open)
addHook('browser.setupMenus', setupMenu)
