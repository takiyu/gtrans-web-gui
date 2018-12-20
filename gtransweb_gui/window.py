# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())

LANGUAGES = {
    'Auto':      'auto',  'Arabic':    'ar', 'Chinese': 'zh-CN',
    'English':   'en',    'Esperanto': 'eo', 'French':  'fr',
    'German':    'de',    'Greek':     'el', 'Italian': 'it',
    'Japanese':  'ja',    'Korean':    'ko', 'Latin':   'la',
    'Portugese': 'pt-PT', 'Russian':   'ru', 'Spanish': 'es',
}
LANGUAGES_INV = {v: k for k, v in LANGUAGES.items()}


class Window(QtWidgets.QMainWindow):
    def __init__(self, trans_func):
        logger.debug('New window is created')
        super(Window, self).__init__()
        self._trans_func = trans_func

        # Set window types
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)
        self.setWindowTitle('GtransWeb')

        # Create GUI parts and layout
        self._gui_parts = GuiParts(parent=self)
        self._gui_layout = GuiLayout(self._gui_parts)
        # Connect event functions
        self._gui_parts.set_connections(self._trans_func, self.swap_langs)

        # GUI configuration
        self._qsettings = QtCore.QSettings('gtransweb-gui', 'window')
        # Load window geometry and state
        self._load_geometry(self._qsettings)
        self._load_langs(self._qsettings)
        self._gui_layout.load_splitter_state(self._qsettings)

        # Set layout
        self._gui_layout.set_root(self)

        # Show window
        self.show()
        self.raise_()

    def get_langs(self):
        ''' Get source and target languages '''
        src = self._gui_parts.src_lang_box.currentText()
        tgt = self._gui_parts.tgt_lang_box.currentText()
        return LANGUAGES[src], LANGUAGES[tgt]

    def set_langs(self, src, tgt):
        ''' Set source and target languages '''
        # Escape `auto` target
        if tgt == 'auto':
            if src == 'ja':
                tgt = 'en'
            else:
                tgt = 'ja'
        # Find indices by text
        src_idx = self._gui_parts.src_lang_box.findText(LANGUAGES_INV[src])
        tgt_idx = self._gui_parts.tgt_lang_box.findText(LANGUAGES_INV[tgt])
        # Set indices
        self._gui_parts.src_lang_box.setCurrentIndex(src_idx)
        self._gui_parts.tgt_lang_box.setCurrentIndex(tgt_idx)

    def get_src_text(self):
        ''' Get text from source text box '''
        return self._gui_parts.src_box.toPlainText()

    def set_src_text(self, text):
        ''' Set text to source text box '''
        self._gui_parts.src_box.setHtml(text)

    def set_tgt_text(self, text):
        ''' Set text to target text box '''
        self._gui_parts.tgt_box.setHtml(text)

    def swap_langs(self):
        ''' Swap source and target languages '''
        src, tgt = self.get_langs()
        self.set_langs(tgt, src)

    def closeEvent(self, event):
        ''' Overridden method to save window states at exit '''
        self._save_geometry(self._qsettings)
        self._save_langs(self._qsettings)
        self._gui_layout.save_splitter_state(self._qsettings)

    def keyPressEvent(self, event):
        ''' Overridden method to handle key inputs '''
        key = event.key()
        if key == QtCore.Qt.Key_Return:
            self._trans_func()
        else:
            super(Window, self).keyPressEvent(event)

    def _load_geometry(self, qsettings):
        geom = qsettings.value('geometry')
        if geom is not None:
            self.restoreGeometry(geom)

    def _save_geometry(self, qsettings):
        qsettings.setValue('geometry', self.saveGeometry())

    def _load_langs(self, qsettings):
        langs = qsettings.value('languages')
        if langs is not None:
            self.set_langs(*langs)
        else:
            self.set_langs('auto', 'ja')  # Set default

    def _save_langs(self, qsettings):
        qsettings.setValue('languages', self.get_langs())


class GuiParts(object):
    def __init__(self, parent):
        # Create Gui widget parts
        self.tgt_box = QtWidgets.QTextEdit(parent)
        self.src_box = QtWidgets.QTextEdit(parent)
        self.swap_btn = QtWidgets.QPushButton("<-->", parent)
        self.src_lang_box = QtWidgets.QComboBox(parent)
        self.tgt_lang_box = QtWidgets.QComboBox(parent)
        self.trans_btn = QtWidgets.QPushButton("Translate", parent)

        # Set part styles
        self._set_styles()

    def set_connections(self, trans_func, swap_langs):
        # Connect functions
        self.trans_btn.clicked.connect(lambda: trans_func())
        self.swap_btn.clicked.connect(lambda: swap_langs())

    def _set_styles(self):
        # Set GUI styles
        self.tgt_box.setReadOnly(True)
        self.tgt_box.setAcceptRichText(True)
        self.src_box.setAcceptRichText(True)
        self.swap_btn.setFixedWidth(50)
        self.src_lang_box.setFixedWidth(90)
        self.tgt_lang_box.setFixedWidth(90)
        self.src_lang_box.addItems(LANGUAGES.keys())
        self.tgt_lang_box.addItems(LANGUAGES.keys())


class GuiLayout(object):
    def __init__(self, gui_parts):
        # Create a splitter for text box
        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self._splitter.addWidget(gui_parts.tgt_box)
        self._splitter.addWidget(gui_parts.src_box)
        self._splitter.setCollapsible(0, False)
        self._splitter.setCollapsible(1, False)

        # Create horizontal bottom layout
        self._bottom_layout = QtWidgets.QHBoxLayout()
        self._bottom_layout.addWidget(gui_parts.src_lang_box)
        self._bottom_layout.addWidget(gui_parts.swap_btn)
        self._bottom_layout.addWidget(gui_parts.tgt_lang_box)
        self._bottom_layout.addWidget(gui_parts.trans_btn)
        # Warp with a widget
        self._bottom_widget = QtWidgets.QWidget()
        self._bottom_widget.setLayout(self._bottom_layout)
        self._bottom_widget.setContentsMargins(-5, -5, -5, -5)

        # Create vertical central layout
        self._central_layout = QtWidgets.QVBoxLayout()
        self._central_layout.addWidget(self._splitter)
        self._central_layout.addWidget(self._bottom_widget)
        # Warp with a widget
        self._central_widget = QtWidgets.QWidget()
        self._central_widget.setLayout(self._central_layout)
        self._central_widget.setContentsMargins(-5, -5, -5, -5)

    def set_root(self, root_widget):
        root_widget.setCentralWidget(self._central_widget)

    def load_splitter_state(self, qsettings):
        state = qsettings.value('splitter_state')
        if state is not None:
            self._splitter.restoreState(state)

    def save_splitter_state(self, qsettings):
        qsettings.setValue('splitter_state', self._splitter.saveState())
