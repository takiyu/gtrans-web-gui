# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtGui, QtCore, QtWidgets

from gtransweb import GTransWebAsync
from clipboard import Clipboard, ClipboardHandler
from callable_buffer import CallableBuffer

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

        def on_clip_changed(src_text):
            select_buf(gtrans_async.translate, 'en', 'ja', src_text)

        def on_trans_finished(tgt_text):
            handler.overwrite_clip(tgt_text)

        clipboard = Clipboard(app)
        handler = ClipboardHandler(clipboard)
        handler.set_callback(on_clip_changed)

        select_buf = CallableBuffer()
        select_buf.set_buftime(3)

        gtrans_async = GTransWebAsync(headless=False)
        gtrans_async.set_callback(on_trans_finished)

        # Start
        app.exec_()


if __name__ == '__main__':
    GTransWebGui()
