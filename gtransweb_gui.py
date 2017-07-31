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
    def __init__(self, title='GtransWeb'):
        logger.debug('New window is created')
        super(GtransPopupWindow, self).__init__()

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

    def set_text(self, text):
        self.textbox.setHtml(text)

    def keyPressEvent(self, event):
        # Exit with escape key
        if event.key() == QtCore.Qt.Key_Escape:
            logger.debug('Hide the window')
            self.hide()


def get_selected_text():
    clip = app.clipboard()
    text = clip.text(QtGui.QClipboard.Selection)
    text = ' '.join(text.splitlines())
    return text.encode('utf-8')


class SelectionChangedHandler():
    def __init__(self, src_lang, tgt_lang, window, width=350, height=150,
                 x_offset=20, y_offset=20, time_offset=1000):
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.window = window
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.time_offset = time_offset
        self.query_deq = collections.deque()
        self.prev_src_text = ''

    def __call__(self):
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
        # Get new selected text
        src_text = get_selected_text()
        if self.prev_src_text == src_text:
            return
        self.prev_src_text = src_text

        # Translate selected text
        logger.debug('Translate selected text')
        tgt_text = gtrans_search(self.src_lang, self.tgt_lang, src_text)
        self.window.set_text(tgt_text)

        # Set window position and size
        if not self.window.isVisible():
            logger.debug('Show the window')
            pos = QtGui.QCursor().pos()
            x, y = pos.x() + self.x_offset, pos.y() + self.y_offset
            self.window.setGeometry(x, y, self.width, self.height)
            # Show
            self.window.show()


if __name__ == '__main__':
    logger.info('Start GtransWeb GUI')

    # Argument
    parser = argparse.ArgumentParser(description='gtrans-web')
    parser.add_argument('--src_lang', type=str, default='auto',
                        help='Source language in `alone` mode')
    parser.add_argument('--tgt_lang', type=str, default='ja',
                        help='Target language in `alone` mode')
    args = parser.parse_args()

    # Text and language information
    src_lang, tgt_lang = args.src_lang, args.tgt_lang

    # Create window and handler
    window = GtransPopupWindow()
    selection_changed_handler = \
        SelectionChangedHandler(src_lang, tgt_lang, window)

    # Set selection changed handler
    clip = app.clipboard()
    clip.selectionChanged.connect(selection_changed_handler)

    # Start
    logger.debug('Wait for selecting')
    app.exec_()
