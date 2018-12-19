# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtGui, QtCore, QtWidgets

from gtransweb import GTransWeb
from clipboard import Clipboard, ClipboardHandler

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class GtransWebGui(object):
    def __init__(self):
        # Qt application
        app = QtWidgets.QApplication([sys.argv[0]])
        # Qt settings
        qsettings = QtCore.QSettings('gtransweb', 'gtanswebgui')

        def callback(src_text):
            print(src_text)
            return f'{src_text}_via_callback'

        clipboard = Clipboard(app)
        handler = ClipboardHandler(clipboard, callback)
        gtrans = GTransWeb(headless=True)

        # Start
        app.exec_()


if __name__ == '__main__':
    pass
