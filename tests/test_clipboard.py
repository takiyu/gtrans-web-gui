# -*- coding: utf-8 -*-
import unittest
import sys

from PyQt5 import QtWidgets

from gtransweb import log_initializer
from gtransweb_gui.clipboard import Clipboard, ClipboardHandler

# logging (root)
from logging import getLogger, DEBUG
log_initializer.set_root_level(DEBUG)
logger = getLogger(__name__)


class ClipboardTest(unittest.TestCase):

    def setUp(self):
        self.app = QtWidgets.QApplication([sys.argv[0]])

    def test_clipboard_mode(self):
        clipboard = Clipboard(self.app)

        # Enumerate modes
        modes = clipboard.get_mode_strs()
        self.assertGreater(len(modes), 0)

        # Clip mode switching
        for mode in modes:
            clipboard.set_mode(mode)
            self.assertEqual(clipboard.get_mode_str(), mode)
            if mode == 'none':
                self.assertEqual(clipboard.get_mode(), None)
            else:
                self.assertIsInstance(clipboard.get_mode(), int)

    def test_clipboard_text(self):
        clipboard = Clipboard(self.app)

        # Clip mode switching
        modes = clipboard.get_mode_strs()
        for mode in modes:
            clipboard.set_mode(mode)

            # Set and get via clipboard
            text = f'test_{mode}_123_てすと_試験'
            clipboard.set_text(text)
            if mode == 'none':
                self.assertEqual(clipboard.get_text(), '')
            else:
                self.assertEqual(clipboard.get_text(), text)

    def test_clipboard_handler(self):
        clipboard = Clipboard(self.app)
        handler = ClipboardHandler(clipboard)

        # Clip mode switching
        modes = clipboard.get_mode_strs()
        for mode in modes:
            clipboard.set_mode(mode)
            self.callback_res = None

            # Define callback and set
            def callback(src_text):
                self.callback_res = f'{src_text}_callback_{mode}'
            handler.set_callback(callback)

            # Make clipboard event happen
            src_text = f'test_{mode}_123_てすと_試験'
            clipboard.set_text(src_text)

            # Check callback result
            if mode == 'none':
                self.assertEqual(self.callback_res, None)
            else:
                self.assertEqual(self.callback_res,
                                 f'{src_text}_callback_{mode}')

            # Check overwriting clipboard via handler dose not affect callback
            handler.overwrite_clip('abc')
            if mode == 'none':
                self.assertEqual(clipboard.get_text(), '')
                self.assertEqual(self.callback_res, None)
            else:
                self.assertEqual(clipboard.get_text(), 'abc')
                self.assertEqual(self.callback_res,
                                 f'{src_text}_callback_{mode}')


if __name__ == '__main__':
    unittest.main()
