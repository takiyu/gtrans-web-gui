#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import collections
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
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
    # app is already created
    app = None


class GtransPopupWindow(QtWidgets.QMainWindow):
    def __init__(self, title='GtransWeb', width=350, height=150, x_offset=20,
                 y_offset=20):
        logger.debug('New window is created')
        super(GtransPopupWindow, self).__init__()

        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset

        # Set window types
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Dialog
        )

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

        # Show
        self.show()

    def set_text(self, text):
        self.textbox.setHtml(text)

    def show_at_cursor(self):
        # Get cursor position
        pos = QtGui.QCursor().pos()
        x, y = pos.x() + self.x_offset, pos.y() + self.y_offset
        self.setGeometry(x, y, self.width, self.height)
        # Show
        self.show()

    def keyPressEvent(self, event):
        # Exit with escape key
        if event.key() == QtCore.Qt.Key_Escape:
            logger.debug('Hide the window')
            self.hide()


def get_clipboard_text(clip_mode, encoding):
    clip = app.clipboard()
    text = clip.text(clip_mode)
    text = ' '.join(text.splitlines())
    return text.encode(encoding)


class ClipboardChangedHandler():
    def __init__(self, clip_mode, src_lang, tgt_lang, encoding, window,
                 time_offset=1000):
        self.clip_mode = clip_mode
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.encoding = encoding
        self.window = window
        self.time_offset = time_offset
        self.query_deq = collections.deque()
        self.prev_src_text = ''

    def __call__(self, mode):
        # Eliminate the clipboard mode
        if mode == self.clip_mode:
            self.query_deq.append(time.time())
            QtCore.QTimer.singleShot(self.time_offset, self._translate)

    def _translate(self):
        # Disable old query
        called_time = self.query_deq.pop()
        if len(self.query_deq) > 0:
            # Overwrite too old query
            if time.time() > called_time + self.time_offset + 1.0:
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
        tgt_text = gtrans_search(self.src_lang, self.tgt_lang, src_text,
                                 self.encoding)
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
    parser.add_argument('--src_lang', type=str, default='auto',
                        help='Source language')
    parser.add_argument('--tgt_lang', type=str, default='ja',
                        help='Target language')
    parser.add_argument('--encoding', type=str, default='utf-8',
                        help='Text encoding used in python str')
    parser.add_argument('--clip_mode', choices=['copy', 'select', 'findbuf'],
                        default='select',
                        help='Clipboard mode for translation trigger')
    args = parser.parse_args()

    # Language information
    src_lang, tgt_lang, encoding = args.src_lang, args.tgt_lang, args.encoding

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

    # Create window and handler
    window = GtransPopupWindow()
    clipboard_changed_handler = ClipboardChangedHandler(clip_mode, src_lang,
                                                        tgt_lang, encoding,
                                                        window)

    # Set clipboard changed handler
    clip = app.clipboard()
    clip.changed.connect(clipboard_changed_handler)

    # Start
    logger.debug('Wait for trigger: %s', args.clip_mode)
    app.exec_()
