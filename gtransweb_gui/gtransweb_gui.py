# -*- coding: utf-8 -*-
import sys
import atexit

from PyQt5 import QtGui, QtCore, QtWidgets

from gtransweb import GTransWebAsync
from clipboard import Clipboard, ClipboardHandler
from callable_buffer import CallableBuffer
from window import Window

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class GTransWebGui(object):
    def __init__(self):
        pass

    def run(self):
        # Qt application
        app = QtWidgets.QApplication([sys.argv[0]])

        window = Window()

        # Qt settings
        qsettings = QtCore.QSettings('gtransweb-gui', 'gtanswebgui')

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
        atexit.register(gtrans_async.exit)

        # Start
        app.exec_()


if __name__ == '__main__':
    GTransWebGui().run()
