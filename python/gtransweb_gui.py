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
#from window import GtransPopupWindow
from window2 import GtransPopupWindowTriple as GtransPopupWindow

# logging
from logging import getLogger, INFO
log_initializer.set_fmt()
log_initializer.set_root_level(INFO)
logger = getLogger(__name__)


# Qt application
if QtCore.QCoreApplication.startingUp():
    # First call
    app = QtWidgets.QApplication([sys.argv[0]])
else:
    # app is already created, so overwrite the following value
    app = None


def get_clipboard_text(clip_mode):
    logger.debug('Get clipboard text (mode: %s)', clip_mode)
    clip = app.clipboard()
    text = clip.text(clip_mode)
    text = ' '.join(text.splitlines())
    try:
        # For python 2
        if isinstance(text, unicode):
            text = text.encode('utf-8')
    except NameError:
        pass
    return text


class ClipboardChangedHandler():
    def __init__(self, clip_mode, window, buf_time):
        self.clip_mode = clip_mode
        self.window = window
        self.buf_time = buf_time
        self.query_deq = collections.deque()

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
        src_text = get_clipboard_text(self.clip_mode)

        # Set window position and size
        if not self.window.isVisible():
            logger.debug('Show the window')
            window.show_at_cursor()

        # Translate clipboard text
        self.window.translate(src_text)


if __name__ == '__main__':
    logger.info('Start GtransWeb GUI')

    # Default argument for each OS
    if os.name == 'posix':
        default_clip_mode = 'select'
        default_buf_time = 1000
    else:
        default_clip_mode = 'copy'
        default_buf_time = 0

    # Argument
    parser = argparse.ArgumentParser(
        description='GtransWebGUI: GUI Helper for Google Translation Website.')
    parser.add_argument('-s', '--src_lang', type=str, default='auto',
                        help='Source language')
    parser.add_argument('-t', '--tgt_lang', type=str, default='ja',
                        help='Target language')
    parser.add_argument('-c', '--clip_mode',  default=default_clip_mode,
                        choices=['copy', 'select', 'findbuf'],
                        help='Clipboard mode for translation trigger')
    parser.add_argument('-b', '--buf_time', type=int, default=default_buf_time,
                        help='Buffering time for clipboard')
    args = parser.parse_args()

    # Language information
    src_lang, tgt_lang = args.src_lang, args.tgt_lang
    buf_time = args.buf_time

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
    clipboard_changed_handler = ClipboardChangedHandler(clip_mode, window,
                                                        buf_time)

    # Set clipboard changed handler
    clip = app.clipboard()
    clip.changed.connect(clipboard_changed_handler)

    # Start
    logger.info('Wait for trigger: %s', args.clip_mode)
    app.exec_()
