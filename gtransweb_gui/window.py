# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets

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
    def __init__(self, trans_func, clip_func, headless_func, clip_modes):
        logger.debug('New window is created')
        super(Window, self).__init__()
        self._trans_func = trans_func
        self._clip_func = clip_func
        self._headless_func = headless_func

        # Set window types
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)
        self.setWindowTitle('GtransWeb')

        # Create GUI parts and layout
        self._gui_parts = GuiParts(self, clip_modes)
        self._gui_layout = GuiLayout(self._gui_parts)
        # Connect event functions
        self._gui_parts.set_connections(self._trans_func, self.swap_langs,
                                        self._clip_func, self._headless_func)

        # GUI configuration
        self._qsettings = QtCore.QSettings('gtransweb-gui', 'window')
        # Load window geometry and state
        self._load_geometry(self._qsettings)
        self._load_langs(self._qsettings)
        self._load_clip_mode(self._qsettings)
        self._load_headless(self._qsettings)
        self._load_overwrite(self._qsettings)
        self._gui_layout.load_splitter_state(self._qsettings)

        # Set layout
        self._gui_layout.set_root(self)

        # Show window
        self.show()
        self.raise_()

    # -------------------------------------------------------------------------
    # ---------------------------- Getter / Setter ----------------------------
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

    def get_clip_mode(self):
        ''' Get clip mode from combo '''
        return self._gui_parts.clip_box.currentText()

    def set_clip_mode(self, mode_str):
        ''' Set clip mode to combo '''
        idx = self._gui_parts.clip_box.findText(mode_str)
        self._gui_parts.clip_box.setCurrentIndex(idx)

    def get_headless(self):
        ''' Get headless mode from checkbox '''
        return bool(self._gui_parts.headless_box.isChecked())

    def set_headless(self, checked):
        ''' Set headless mode to checkbox '''
        self._gui_parts.headless_box.setChecked(bool(checked))

    def get_overwrite(self):
        ''' Get overwriting mode from checkbox '''
        return bool(self._gui_parts.overwrite_box.isChecked())

    def set_overwrite(self, checked):
        ''' Set overwriting mode to checkbox '''
        self._gui_parts.overwrite_box.setChecked(bool(checked))

    # -------------------------------------------------------------------------
    # --------------------------- Overridden methods --------------------------
    def closeEvent(self, event):
        ''' Overridden method to save window states at exit '''
        self._save_geometry(self._qsettings)
        self._save_langs(self._qsettings)
        self._save_clip_mode(self._qsettings)
        self._save_headless(self._qsettings)
        self._save_overwrite(self._qsettings)
        self._gui_layout.save_splitter_state(self._qsettings)

    def keyPressEvent(self, event):
        ''' Overridden method to handle key inputs '''
        key = event.key()
        if key == QtCore.Qt.Key_Return:
            self._trans_func()
        else:
            super(Window, self).keyPressEvent(event)

    # -------------------------------------------------------------------------
    # ----------------------------- Loader / Saver ----------------------------
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

    def _load_clip_mode(self, qsettings):
        mode = qsettings.value('clip_mode')
        if mode is not None:
            self.set_clip_mode(mode)
        else:
            self.set_clip_mode('copy')  # set default

    def _save_clip_mode(self, qsettings):
        qsettings.setValue('clip_mode', self.get_clip_mode())

    def _load_headless(self, qsettings):
        mode = qsettings.value('headless')
        if mode is not None:
            self.set_headless(mode == 'true')
        else:
            self.set_headless(True)  # Set default

    def _save_headless(self, qsettings):
        qsettings.setValue('headless', self.get_headless())

    def _load_overwrite(self, qsettings):
        mode = qsettings.value('overwrite')
        if mode is not None:
            self.set_overwrite(mode == 'true')
        else:
            self.set_overwrite(True)  # Set default

    def _save_overwrite(self, qsettings):
        qsettings.setValue('overwrite', self.get_overwrite())


class GuiParts(object):
    def __init__(self, parent, clip_modes):
        # Create Gui widget parts
        # Splitter
        self.tgt_box = QtWidgets.QTextEdit(parent)
        self.src_box = QtWidgets.QTextEdit(parent)

        # 1st row
        self.src_lang_box = QtWidgets.QComboBox(parent)
        self.tgt_lang_box = QtWidgets.QComboBox(parent)
        self.swap_btn = QtWidgets.QPushButton('<-->', parent)
        self.trans_btn = QtWidgets.QPushButton('Translate', parent)

        # 2nd row
        self.clip_box = QtWidgets.QComboBox(parent)
        self.headless_box = QtWidgets.QCheckBox('Headless browser', parent)
        self.overwrite_box = QtWidgets.QCheckBox('Overwrite clipboard', parent)

        # Set part styles
        self._set_styles(clip_modes)

    def set_connections(self, trans_func, swap_langs, clip_func,
                        headless_func):
        # Connect functions
        self.trans_btn.clicked.connect(lambda: trans_func())
        self.swap_btn.clicked.connect(lambda: swap_langs())
        self.clip_box.currentTextChanged.connect(clip_func)
        self.headless_box.clicked.connect(headless_func)

    def _set_styles(self, clip_modes):
        # Set GUI styles
        self.tgt_box.setReadOnly(True)
        self.tgt_box.setAcceptRichText(True)
        self.src_box.setAcceptRichText(True)

        self.src_lang_box.setFixedWidth(90)
        self.tgt_lang_box.setFixedWidth(90)
        self.src_lang_box.addItems(LANGUAGES.keys())
        self.tgt_lang_box.addItems(LANGUAGES.keys())
        self.swap_btn.setFixedWidth(50)

        self.clip_box.addItems(clip_modes)
        self.clip_box.setFixedWidth(90)

        self.headless_box.setFixedWidth(140)


class GuiLayout(object):
    def __init__(self, gui_parts):
        # Create a splitter for text box
        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self._splitter.addWidget(gui_parts.tgt_box)
        self._splitter.addWidget(gui_parts.src_box)
        self._splitter.setCollapsible(0, False)
        self._splitter.setCollapsible(1, False)

        # Create horizontal bottom layout (row1)
        self._row1_layout = QtWidgets.QHBoxLayout()
        self._row1_layout.addWidget(gui_parts.src_lang_box)
        self._row1_layout.addWidget(gui_parts.swap_btn)
        self._row1_layout.addWidget(gui_parts.tgt_lang_box)
        self._row1_layout.addWidget(gui_parts.trans_btn)
        self._row1_layout.setContentsMargins(0, 0, 0, 0)
        # Warp with a widget
        self._row1_widget = QtWidgets.QWidget()
        self._row1_widget.setLayout(self._row1_layout)
        self._row1_widget.setContentsMargins(-3, -3, -3, -3)

        # Create horizontal bottom layout (row2)
        self._row2_layout = QtWidgets.QHBoxLayout()
        self._row2_layout.addWidget(gui_parts.clip_box)
        self._row2_layout.addWidget(gui_parts.headless_box)
        self._row2_layout.addWidget(gui_parts.overwrite_box)
        self._row2_layout.setContentsMargins(0, 0, 0, 0)
        # Warp with a widget
        self._row2_widget = QtWidgets.QWidget()
        self._row2_widget.setLayout(self._row2_layout)
        self._row2_widget.setContentsMargins(-3, -3, -3, -3)

        # Create vertical central layout
        self._central_layout = QtWidgets.QVBoxLayout()
        self._central_layout.addWidget(self._splitter)
        self._central_layout.addWidget(self._row1_widget)
        self._central_layout.addWidget(self._row2_widget)
        self._central_layout.setContentsMargins(5, 5, 5, 5)
        # Warp with a widget
        self._central_widget = QtWidgets.QWidget()
        self._central_widget.setLayout(self._central_layout)

    def set_root(self, root_widget):
        root_widget.setCentralWidget(self._central_widget)

    def load_splitter_state(self, qsettings):
        state = qsettings.value('splitter_state')
        if state is not None:
            self._splitter.restoreState(state)

    def save_splitter_state(self, qsettings):
        qsettings.setValue('splitter_state', self._splitter.saveState())
