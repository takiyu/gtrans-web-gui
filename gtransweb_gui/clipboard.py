# -*- coding: utf-8 -*-
from collections import OrderedDict

from PyQt5 import QtGui

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class ClipboardHandler:
    def __init__(self, clipboard):
        self._clipboard = clipboard

        self._callback = None
        self._skip_str = None  # Flag and string for escaping recursing

        # Connect event handling
        self._clipboard.connect(self)

    def set_callback(self, callback):
        ''' Set callback which is call when clipboard changed
            :param callback: Callback function. It must perform
                             `callback(src_text)`.
        '''
        self._callback = callback

    def overwrite_clip(self, text):
        # Set for escaping recursive calling
        self._skip_str = text
        # Overwrite
        self._clipboard.set_text(text)

    def __call__(self, mode):
        ''' Entry point of changing event handling '''
        # Eliminate the clipboard mode
        if mode != self._clipboard.get_mode():
            return

        # Get current clipboard text
        src_text = self._clipboard.get_text()

        # Escape recursive calling (reset flag and skip when text is same)
        if self._skip_str is not None:
            skip = (self._skip_str == src_text)
            self._skip_str = None
            if skip:
                return

        # Run callback
        if callable(self._callback):
            self._callback(src_text)


class Clipboard:

    def __init__(self, app):
        self._clip = app.clipboard()

        # Clipboard mode enumerates
        self._modes = _enum_clip_modes(self._clip)
        self._modes_inv = {v: k for k, v in self._modes.items()}

        # Set default mode
        self._mode = self._modes['copy']

    def get_mode(self):
        ''' Return clipboard mode enum variable '''
        return self._mode

    def get_mode_str(self):
        ''' Return clipboard mode string '''
        return self._modes_inv[self._mode]

    def get_mode_strs(self):
        ''' Return available clipboard mode strings '''
        return tuple(self._modes.keys())

    def set_mode(self, mode_str):
        ''' Set clipboard mode by mode string '''
        try:
            self._mode = self._modes[mode_str]
        except KeyError:
            logger.error(f'Invalid clipboard mode ({mode_str})')

    def get_text(self):
        ''' Get text in the clipboard (When the mode is 'none', do nothing)'''
        if self._mode is None:
            return ''
        else:
            return _get_clip_text(self._clip, self._mode, self.get_mode_str())

    def set_text(self, text):
        ''' Set text to the clipboard (When the mode is 'none', do nothing)'''
        if self._mode is None:
            return
        else:
            _set_clip_text(self._clip, self._mode, text, self.get_mode_str())

    def connect(self, handler):
        ''' Set clipboard changed handler '''
        self._clip.changed.connect(handler)


def _enum_clip_modes(clip):
    ''' Enumerate available clipboard modes '''
    modes = OrderedDict()
    modes['none'] = None
    modes['copy'] = QtGui.QClipboard.Clipboard  # Common for all OS
    if clip.supportsSelection():
        modes['select'] = QtGui.QClipboard.Selection  # Mostly Linux
    if clip.supportsFindBuffer():
        modes['findbuf'] = QtGui.QClipboard.FindBuffer  # MacOS
    return modes


def _get_clip_text(clip, mode, mode_str=''):
    ''' Get text in the clipboard '''
    logger.debug(f'Get clipboard text (mode: {mode} {mode_str})')
    text = clip.text(mode)
    try:
        # For python 2
        if isinstance(text, unicode):
            text = text.encode('utf-8')
    except NameError:
        pass
    return text


def _set_clip_text(clip, mode, text, mode_str=''):
    ''' Set text to the clipboard '''
    logger.debug(f'Set clipboard text (mode: {mode} {mode_str})')
    clip.setText(text, mode=mode)
    return text
