# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        logger.debug('New window is created')
        super(Window, self).__init__()

        # Set window types
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)
        self.setWindowTitle('GtransWeb')

        self._qsettings = QtCore.QSettings('gtransweb-gui', 'window')

        self._init_gui()

        self.show()
        self.raise_()

    def closeEvent(self, event):
        # Save window geometry and state
        self._qsettings.setValue("geometry", self.saveGeometry())
        self._qsettings.setValue("splitter_state", self.splitter.saveState())

    def _init_gui(self):
        # Create a target text box
        self.tgt_box = QtWidgets.QTextEdit(self)
        self.tgt_box.setReadOnly(True)
        self.tgt_box.setAcceptRichText(True)
        # Create a source text box
        self.src_box = QtWidgets.QTextEdit(self)
        self.src_box.setAcceptRichText(True)
        # Create bottom items
        self.src_lang_box = QtWidgets.QLineEdit(self)
        self.tgt_lang_box = QtWidgets.QLineEdit(self)
        self.src_lang_box.setFixedWidth(50)
        self.tgt_lang_box.setFixedWidth(50)
        # show candidate list when clicked
#         self.src_lang_box.focusInEvent = lambda _: self._show_candidates(1)
#         self.tgt_lang_box.focusInEvent = lambda _: self._show_candidates(2)
        self.swap_btn = QtWidgets.QPushButton("<-->", self)
        self.swap_btn.setFixedWidth(50)
#         self.swap_btn.clicked.connect(self._swap_langs)
        self.trans_btn = QtWidgets.QPushButton("Translate", self)
        self.trans_btn.clicked.connect(lambda: self.translate())

        # Create a splitter for text box
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.tgt_box)
        self.splitter.addWidget(self.src_box)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        # Create horizontal bottom layout
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.bottom_layout.addWidget(self.src_lang_box)
        self.bottom_layout.addWidget(self.swap_btn)
        self.bottom_layout.addWidget(self.tgt_lang_box)
        self.bottom_layout.addWidget(self.trans_btn)
        # Warp with a widget
        self.bottom_widget = QtWidgets.QWidget()
        self.bottom_widget.setLayout(self.bottom_layout)
        self.bottom_widget.setContentsMargins(-5, -5, -5, -5)

        # Create vertical central layout
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addWidget(self.splitter)
        self.central_layout.addWidget(self.bottom_widget)
        # Warp with a widget
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.central_layout)
        self.central_widget.setContentsMargins(-5, -5, -5, -5)

        # Set layout
        self.setCentralWidget(self.central_widget)
