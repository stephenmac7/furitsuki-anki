# coding=utf-8
import subprocess
from anki.hooks import addHook

CONFIG = {
    'srcFields': ['Expression'],
    'dstFields': ['Reading'],
}

JAR_FILE = '../../addons/furitsuki/furitsuki.jar'
PROC_ARGS = ['java', '-jar', JAR_FILE]

class FuritsukiController:
    def __init__(self):
        self.proc = None

    def ensure_open(self):
        if not self.proc:
            self.proc = subprocess.Popen(PROC_ARGS, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def reading(self, text):
        self.ensure_open()
        self.proc.stdin.write(text.replace('\n', ' ').encode('utf-8')) # Make sure we only have one line
        self.proc.stdin.write(u'\n')
        self.proc.stdin.flush()
        return unicode(self.proc.stdout.readline(), 'utf-8')

# Shamelessly copied from the Japanese support plugin -- but this is GPL so it's all good
def onFocusLost(flag, n, fidx):
    global furitsuki
    from aqt import mw
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
        n[dst] = u'Loading...'
        n.flush()
        n[dst] = furitsuki.reading(srcTxt)
    except Exception, e:
        furitsuki = None
        raise
    return True

# Init
furitsuki = FuritsukiController()
addHook('editFocusLost', onFocusLost)
