# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets

from gtransweb import gtrans_search

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class GtransPopupWindow(QtWidgets.QMainWindow):
    def __init__(self, qsettings, src_lang, tgt_lang, title='GtransWeb',
                 curpos_offset=(20, 20), default_size=(350, 150)):
        logger.debug('New window is created')
        super(GtransPopupWindow, self).__init__()

        # Set window types
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog)

        # Window title
        self.setWindowTitle(title)

        # Set GUI items
        self._init_gui()
        self._init_candidate_list()

        # Store arguments
        self.qsettings = qsettings
        self.curpos_offset = curpos_offset
        self._set_langs(src_lang, tgt_lang)

        # Previous status to prevent from multiple translation
        self.prev_src_text = ''
        self.prev_src_lang = ''
        self.prev_tgt_lang = ''

        # Set window size posoiShow
        geom = self.qsettings.value("geometry")
        if geom is None:
            self.resize(default_size[0], default_size[1])
            self.show_at_cursor()
        else:
            self.restoreGeometry(geom)
            self.show()
            self.cand_list.hide()  # I don't want this popping up on init
            self.raise_()
        # Restore saved state if possible
        splitter_state = self.qsettings.value("splitter_state")
        if splitter_state is not None:
            self.splitter.restoreState(splitter_state)

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
        self.src_lang_box.focusInEvent = lambda _: self._show_candidates(1)
        self.tgt_lang_box.focusInEvent = lambda _: self._show_candidates(2)
        self.swap_btn = QtWidgets.QPushButton("<-->", self)
        self.swap_btn.setFixedWidth(50)
        self.swap_btn.clicked.connect(self._swap_langs)
        self.trans_btn = QtWidgets.QPushButton("Translate", self)
        self.trans_btn.clicked.connect(lambda: self.translate())

        # Create a splitter for text box
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.tgt_box)
        self.splitter.addWidget(self.src_box)

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

    def _init_candidate_list(self):
        self.cand_list = QtWidgets.QListWidget(self)

        # Double click or press enter to insert
        self.cand_list.itemDoubleClicked.connect(self._set_from_list)
        self.cand_list.focusOutEvent = lambda _: self.cand_list.hide()

        # The abbreviation for that language
        self.candidates = {
                "Auto": "auto", "Arabic": "ar", "Chinese": "zh-CN",
                "English": "en", "Esperanto": "eo", "French": "fr",
                "German": "de", "Greek": "el", "Italian": "it",
                "Japanese": "ja", "Korean": "ko", "Latin": "la",
                "Portugese": "pt-PT", "Russian": "ru", "Spanish": "es",
        }

        for candidate in self.candidates.keys():
            QtWidgets.QListWidgetItem(candidate, self.cand_list)

        self.cand_list.setGeometry(100, 100, 250, 300)

    def _show_candidates(self, box_selected):
        logger.debug("show_candidates")
        self.box_selected = box_selected
        self.cand_list.show()
        self.cand_list.setFocus()

    def _set_from_list(self):
        item = self.cand_list.currentItem().text()
        lang = self.candidates[item]
        if self.box_selected is 1:
            logger.debug("src_lang -> " + lang)
            self.src_lang_box.setText(lang)
            self.cand_list.hide()
        elif self.box_selected is 2:
            logger.debug("tgt_lang -> " + lang)
            self.tgt_lang_box.setText(lang)
            self.cand_list.hide()

    def _set_langs(self, src_lang, tgt_lang):
        self.src_lang_box.setText(src_lang)
        self.tgt_lang_box.setText(tgt_lang)

    def _get_langs(self):
        src_lang = self.src_lang_box.text()
        tgt_lang = self.tgt_lang_box.text()
        return src_lang, tgt_lang

    def _swap_langs(self):
        src_lang, tgt_lang = self._get_langs()
        if src_lang == 'auto':  # Specific pattern for practical usage
            src_lang = 'en'
        self._set_langs(tgt_lang, src_lang)

    def translate(self, src_text=None):
        if src_text is None:
            # Fetch source text from GUI
            logger.debug('Translate the text in tgt_box')
            src_text = self.src_box.toPlainText()
        else:
            # Set passed source text to GUI
            logger.debug('Translate the passed text')
            self.src_box.setHtml(src_text)
        src_lang, tgt_lang = self._get_langs()
        # Check previous status
        if src_text == self.prev_src_text and \
           src_lang == self.prev_src_lang and \
           tgt_lang == self.prev_tgt_lang:
            logger.debug('Skip because of previous status')
            return
        if src_text == '':
            logger.debug('Skip empty text')
            return
        self.prev_src_text, self.prev_src_lang, self.prev_tgt_lang = \
            src_text, src_lang, tgt_lang
        # Translate
        tgt_text = gtrans_search(src_lang, tgt_lang, src_text)
        logger.debug('Finish to translate')
        # Set target text to GUI
        self.tgt_box.setHtml(tgt_text)

    def show_at_cursor(self):
        # Get cursor position and move
        pos = QtGui.QCursor().pos()
        x, y = pos.x() + self.curpos_offset[0], pos.y() + self.curpos_offset[1]
        self.move(x, y)
        # Show
        self.show()
        self.raise_()

    def keyPressEvent(self, event):
        # Exit with escape key
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            logger.debug('Hide the window')
            self.hide()
        elif key == QtCore.Qt.Key_Return:
            if not self.cand_list.isHidden():
                self._set_from_list()
            else:
                self.translate()
        else:
            super(GtransPopupWindow, self).keyPressEvent(event)

    def closeEvent(self, event):
        # Save window geometry and state
        self.qsettings.setValue("geometry", self.saveGeometry())
        self.qsettings.setValue("splitter_state", self.splitter.saveState())
