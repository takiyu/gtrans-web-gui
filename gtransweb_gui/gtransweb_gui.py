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
        # Qt application
        self._app = QtWidgets.QApplication([sys.argv[0]])

        # Main window
        self._window = Window(self._translate)
        # Clipboard and its handler
        self._clipboard = Clipboard(self._app)
        self._clip_handler = ClipboardHandler(self._clipboard)
        self._clip_handler.set_callback(self._on_clip_changed)
        # Translation engine
        self._gtrans_async = GTransWebAsync(headless=True)
        self._gtrans_async.set_callback(self._on_trans_finished)
        atexit.register(self._gtrans_async.exit)
        # Buffer for selection mode
        self._select_buf = CallableBuffer()
        self._select_buf.set_buftime(3)

        # Qt settings
        qsettings = QtCore.QSettings('gtransweb-gui', 'gtanswebgui')

    def run(self):
        ''' Run main application '''
        self._app.exec_()

    def _translate(self, src_text=None):
        ''' Translate passed text. If not passed, it will be get from GUI. '''
        # Get languages from GUI
        src_lang, tgt_lang = self._window.get_langs()
        # Source text
        if src_text is None:
            # Get text from GUI
            src_text = self._window.get_src_text()
        else:
            # Set text to GUI
            self._window.set_src_text(src_text)
        # Start translation
        self._gtrans_async.translate(src_lang, tgt_lang, src_text)

    def _on_clip_changed(self, src_text):
        ''' When clipboard changed, start to translate. '''
        if self._clipboard.get_mode_str() == 'select':
            # Postpone by buffering
            self._select_buf(self._translate, src_text)
        else:
            # Translate right now
            self._translate(src_text)

    def _on_trans_finished(self, tgt_text):
        ''' When translation finished, set to GUI and clipboard. '''
        # Set to GUI
#         self._window.set_tgt_text(tgt_text)
        # Set to clipboard
        self._clip_handler.overwrite_clip(tgt_text)


if __name__ == '__main__':
    GTransWebGui().run()
