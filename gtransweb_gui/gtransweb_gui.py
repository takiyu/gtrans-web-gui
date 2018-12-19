# -*- coding: utf-8 -*-
import sys
from queue import Queue

from PyQt5 import QtGui, QtCore, QtWidgets

from gtransweb import GTransWebAsync
from clipboard import Clipboard, ClipboardHandler

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class GTransWebGui(object):
    def __init__(self):
        # Qt application
        app = QtWidgets.QApplication([sys.argv[0]])
        # Qt settings
        qsettings = QtCore.QSettings('gtransweb', 'gtanswebgui')

        gtrans_async = GTransWebAsync(headless=True)
        clipboard = Clipboard(app)
        handler = ClipboardHandler(clipboard)

        q = Queue()

        def clip_callback(src_text):
            gtrans_async.translate('en', 'ja', src_text)
            # return None
            return q.get()

        def gtrans_callback(tgt_text):
            print(tgt_text)
            q.put(tgt_text)

        handler.set_callback(clip_callback)
        gtrans_async.set_callback(gtrans_callback)

        # Start
        app.exec_()


if __name__ == '__main__':
    GTransWebGui()
