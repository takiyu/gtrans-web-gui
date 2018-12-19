# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        # Set window types
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)
