# -*- coding: utf-8 -*-
from PyQt5 import QtGui

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class ClipboardHandler(object):
    def __init__(self, clipboard):
        self._clipboard = clipboard

        self._callback = None
        self._overwrite_flag = True
        self._skip_flag = False  # Flag for escaping recursing

        # Connect event handling
        self._clipboard.connect(self)

    def set_callback(self, callback):
        ''' Set callback which is call when clipboard changed
            :param callback: Callback function. It must perform
                             `tgt_text = callback(src_text)`. If `tgt_text` is
                             not string, no overwriting will be happen.
        '''
        self._callback = callback

    def get_overwrite_flag(self):
        ''' Get a flag for clipboard overwriting '''
        return self._overwrite_flag

    def set_overwrite_flag(self, flag):
        ''' Set a flag for clipboard overwriting '''
        self._overwrite_flag = flag

    def __call__(self, mode):
        ''' Entry point of changing event handling '''
        if not callable(self._callback):
            return

        # Eliminate the clipboard mode
        if mode != self._clipboard.get_mode():
            return

        # Escape recursive calling
        if self._skip_flag:
            self._skip_flag = False
            return

        # Run callback
        src_text = self._clipboard.get_text()
        tgt_text = self._callback(src_text)
        if self._overwrite_flag and isinstance(tgt_text, str):
            self._skip_flag = True  # Set for escaping recursive calling
            self._clipboard.set_text(tgt_text)


class Clipboard(object):

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
        ''' Get text in the clipboard '''
        return _get_clip_text(self._clip, self._mode, self.get_mode_str())

    def set_text(self, text):
        ''' Set text to the clipboard '''
        _set_clip_text(self._clip, self._mode, text, self.get_mode_str())

    def connect(self, handler):
        ''' Set clipboard changed handler '''
        self._clip.changed.connect(handler)


def _enum_clip_modes(clip):
    ''' Enumerate available clipboard modes '''
    modes = {'copy': QtGui.QClipboard.Clipboard}  # Common for all OS
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
