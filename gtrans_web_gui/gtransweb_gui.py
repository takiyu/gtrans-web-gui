#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import collections
import os
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
from threading import Thread
import time

from gtrans_web import log_initializer

from window import GtransPopupWindow
from window2 import GtransPopupWindowDouble

# logging (root)
from logging import getLogger, INFO
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


def set_clipboard_text(clip_mode, text):
    logger.debug('Set clipboard text (mode: %s)', clip_mode)
    clip = app.clipboard()
    clip.setText(text, mode=clip_mode)
    return text


class ClipboardChangedHandler():

    def __init__(self, clip_mode, window, buf_time, overwrite_mode):
        self.clip_mode = clip_mode
        self.window = window
        self.buf_time = buf_time
        self.query_deq = collections.deque()
        self.translation_skip = False
        self.overwrite_mode = overwrite_mode

    def __call__(self, mode):
        # Eliminate the clipboard mode
        if mode == self.clip_mode:
            self.query_deq.append(time.time())
            QtCore.QTimer.singleShot(self.buf_time, self._translate)

    def _translate(self):
        # Disable old query
        called_time = self.query_deq.pop()

        # Not to translate translated text again
        if self.translation_skip:
            logger.debug('Translation is skipped')
            self.translation_skip = False
            return

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
        tgt_text = self.window.translate(src_text)

        # Overwrite original text on the clipboard with translated
        if self.overwrite_mode:
            self.translation_skip = True
            set_clipboard_text(self.clip_mode, tgt_text)


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
    parser.add_argument('-m', '--middle_lang', type=str, default='en',
                        help='Intermediate language (for secondhand translation)')
    parser.add_argument('-c', '--clip_mode',  default=default_clip_mode,
                        choices=['copy', 'select', 'findbuf'],
                        help='Clipboard mode for translation trigger')
    parser.add_argument('-b', '--buf_time', type=int, default=default_buf_time,
                        help='Buffering time for clipboard')
    parser.add_argument('-d', '--double', action='store_true',
                        help='Secondhand translation.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Overwrite clipboard with translated text')
    args = parser.parse_args()

    # Language information
    src_lang, middle_lang, tgt_lang = \
        args.src_lang, args.middle_lang, args.tgt_lang
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
    if args.double:
        window = GtransPopupWindowDouble(
            qsettings, src_lang, tgt_lang, middle_lang)
    else:
        window = GtransPopupWindow(qsettings, src_lang, tgt_lang)
    clipboard_changed_handler = ClipboardChangedHandler(clip_mode, window,
                                                        buf_time, args.overwrite)

    # Set clipboard changed handler
    clip = app.clipboard()
    clip.changed.connect(clipboard_changed_handler)

    # Start
    logger.info('Wait for trigger: %s', args.clip_mode)
    app.exec_()
