#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import collections
import os
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
from threading import Thread
import time

import log_initializer
from gtransweb import gtrans_search

# logging
from logging import getLogger, DEBUG
log_initializer.set_fmt()
log_initializer.set_root_level(DEBUG)
logger = getLogger(__name__)


# Qt application
if QtCore.QCoreApplication.startingUp():
    # First call
    app = QtWidgets.QApplication([sys.argv[0]])
else:
    # app is already created, so overwrite the following value
    app = None


class GtransPopupWindow(QtWidgets.QMainWindow):
    def __init__(self, qsettings, title='GtransWeb', curpos_offset=(20, 20),
                 default_size=(350, 150)):
        logger.debug('New window is created')
        super(GtransPopupWindow, self).__init__()

        # Store arguments
        self.qsettings = qsettings
        self.curpos_offset = curpos_offset

        # Set window types
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)

        # Window title
        self.setWindowTitle(title)

        # Create Text box
        self.textbox = QtWidgets.QTextEdit(self)
        self.textbox.setReadOnly(True)
        self.textbox.setAcceptRichText(True)

        # Put text box
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addWidget(self.textbox)
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.central_layout)
        self.central_widget.setContentsMargins(-5, -5, -5, -5)
        self.setCentralWidget(self.central_widget)

        # Set window size posoiShow
        geom = self.qsettings.value("geometry")
        if geom is None:
            self.resize(default_size[0], default_size[1])
            self.show_at_cursor()
        else:
            self.restoreGeometry(geom)
            self.show()
            self.raise_()

    def set_text(self, text):
        self.textbox.setHtml(text)

    def show_at_cursor(self):
        # Get cursor position and move
        pos = QtGui.QCursor().pos()
        x, y = pos.x() + self.curpos_offset[0], pos.y() + self.curpos_offset[1]
        self.move(x, y)
        # Show
        self.show()
        self.raise_()

    def keyPressEvent(self, event):
        # Exit with escape key
        if event.key() == QtCore.Qt.Key_Escape:
            logger.debug('Hide the window')
            self.hide()

    def closeEvent(self, event):
        # Save current window size and position
        self.qsettings.setValue("geometry", self.saveGeometry())


def get_clipboard_text(clip_mode, encoding):
    clip = app.clipboard()
    text = clip.text(clip_mode)
    text = ' '.join(text.splitlines())
    return text.encode(encoding)


class ClipboardChangedHandler():
    def __init__(self, clip_mode, src_lang, tgt_lang, encoding, window,
                 buf_time):
        self.clip_mode = clip_mode
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.encoding = encoding
        self.window = window
        self.buf_time = buf_time
        self.query_deq = collections.deque()
        self.prev_src_text = ''

    def __call__(self, mode):
        # Eliminate the clipboard mode
        if mode == self.clip_mode:
            self.query_deq.append(time.time())
            QtCore.QTimer.singleShot(self.buf_time, self._translate)

    def _translate(self):
        # Disable old query
        called_time = self.query_deq.pop()
        if len(self.query_deq) > 0:
            # Overwrite too old query
            if time.time() > called_time + self.buf_time + 1.0:
                self.query_deq.clear()
            else:
                return
        # Get new clipboard text
        src_text = get_clipboard_text(self.clip_mode, self.encoding)
        if self.prev_src_text == src_text:
            return
        self.prev_src_text = src_text

        # Translate clipboard text
        logger.debug('Translate the text in clipboard')
        tgt_text = gtrans_search(self.src_lang, self.tgt_lang, src_text)
        self.window.set_text(tgt_text)

        # Set window position and size
        if not self.window.isVisible():
            logger.debug('Show the window')
            window.show_at_cursor()


if __name__ == '__main__':
    logger.info('Start GtransWeb GUI')

    # Argument
    parser = argparse.ArgumentParser(
        description='GtransWebGUI: GUI Helper for Google Translation Website.')
    parser.add_argument('-s', '--src_lang', type=str, default='auto',
                        help='Source language')
    parser.add_argument('-t', '--tgt_lang', type=str, default='ja',
                        help='Target language')
    parser.add_argument('--encoding', type=str, default='utf-8',
                        help='Text encoding used in python str for input')
    parser.add_argument('-c', '--clip_mode',  default='select',
                        choices=['copy', 'select', 'findbuf'],
                        help='Clipboard mode for translation trigger')
    parser.add_argument('-b', '--buf_time', type=int, default=1000,
                        help='Buffering time for clipboard')
    args = parser.parse_args()

    # Language information
    src_lang, tgt_lang = args.src_lang, args.tgt_lang
    encoding, buf_time = args.encoding, args.buf_time

    # Clipboard mode
    if args.clip_mode == 'copy':
        clip_mode = QtGui.QClipboard.Clipboard
    elif args.clip_mode == 'select':
        clip_mode = QtGui.QClipboard.Selection
    elif args.clip_mode == 'findbuf':
        clip_mode = QtGui.QClipboard.FindBuffer
    else:
        logger.error('Unknown clip_mode: %d', args.clip_mode)
        exit(1)

    # Qt settings
    qsettings = QtCore.QSettings('gtransweb', 'gtanswebgui')

    # Create window and handler
    window = GtransPopupWindow(qsettings)
    clipboard_changed_handler = ClipboardChangedHandler(clip_mode, src_lang,
                                                        tgt_lang, encoding,
                                                        window, buf_time)

    # Set clipboard changed handler
    clip = app.clipboard()
    clip.changed.connect(clipboard_changed_handler)

    # Start
    logger.debug('Wait for trigger: %s', args.clip_mode)
    app.exec_()
