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
    def __init__(self, qsettings, src_lang, tgt_lang, title='GtransWeb', curpos_offset=(20, 20),
                 default_size=(350, 150)):
        logger.debug('New window is created')
        super(GtransPopupWindow, self).__init__()
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

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

        self.textbox2 = MyTextEdit(self)
        self.textbox2.setFixedHeight(100)

        self.src_box = QtWidgets.QTextEdit(self)
        self.src_box.setPlainText(self.src_lang)
        self.src_box.setFixedHeight(40)
        self.tgt_box = QtWidgets.QTextEdit(self)
        self.tgt_box.setPlainText(self.tgt_lang)
        self.tgt_box.setFixedHeight(40)
        self.btn2 = QtWidgets.QPushButton("<-->", self)
        self.btn2.clicked.connect(self.toggle_src_tgt)
        self.btn2.setFixedWidth(100)
        self.btn3 = QtWidgets.QPushButton("change", self)
        self.btn3.clicked.connect(self.set_src_tgt)

        # Put text box
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.bottom_layout.addWidget(self.src_box)
        self.bottom_layout.addWidget(self.btn2)
        self.bottom_layout.addWidget(self.tgt_box)
        self.bottom_layout.addWidget(self.btn3)

        self.bottom_widget = QtWidgets.QWidget()
        self.bottom_widget.setLayout(self.bottom_layout)
        self.bottom_widget.setContentsMargins(-5, -5, -5, -5)
        self.bottom_widget.setFixedHeight(60)

        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addWidget(self.textbox)
        self.central_layout.addWidget(self.textbox2)
        self.central_layout.addWidget(self.bottom_widget)

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

    def set_text2(self, text):
        self.textbox2.setPlainText(text)

    def translate_from_textbox(self):
        logger.debug('Translate the text in textbox')
        src_text = self.textbox2.toPlainText()
        tgt_text = gtrans_search(self.src_lang, self.tgt_lang, src_text)
        self.set_text(tgt_text)

    def toggle_src_tgt(self):
        tmp = self.src_lang
        self.src_lang = self.tgt_lang
        self.tgt_lang = tmp
        self.src_box.setText(self.src_lang)
        self.tgt_box.setText(self.tgt_lang)
        logger.debug("src: {0} tgt: {1}".format(self.src_lang, self.tgt_lang))

    def set_src_tgt(self):
        self.src_lang = self.src_box.toPlainText()
        self.tgt_lang = self.tgt_box.toPlainText()
        logger.debug("src: {0} tgt: {1}".format(self.src_lang, self.tgt_lang))

    def get_src_lang(self):
        return self.src_lang

    def get_tgt_lang(self):
        return self.tgt_lang

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


class MyTextEdit(QtWidgets.QTextEdit):
    def __init__(self, window):
        super(QtWidgets.QTextEdit, self).__init__()
        self.window = window

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.window.translate_from_textbox()
        else:
            super().keyPressEvent(event)


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
        self.src_lang = self.window.get_src_lang()
        self.tgt_lang = self.window.get_tgt_lang()
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
        self.window.set_text2(src_text.decode(self.encoding))

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
    parser.add_argument('-c', '--clip_mode',  default='copy',
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
    window = GtransPopupWindow(qsettings, src_lang, tgt_lang)
    clipboard_changed_handler = ClipboardChangedHandler(clip_mode, src_lang,
                                                        tgt_lang, encoding,
                                                        window, buf_time)

    # Set clipboard changed handler
    clip = app.clipboard()
    clip.changed.connect(clipboard_changed_handler)

    # Start
    logger.debug('Wait for trigger: %s', args.clip_mode)
    app.exec_()
