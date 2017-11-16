# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets

from gtransweb import gtrans_search
from window import GtransPopupWindow
# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class GtransPopupWindowDouble(GtransPopupWindow):

    def _init_memory(self):
        # Previous status to prevent from multiple translation
        self.prev_src_text = ''
        self.prev_src_lang = ''
        self.prev_middle_text = ''
        self.prev_middle_lang = ''
        self.prev_tgt_lang = ''

    def _init_gui(self):
        self.is_double = True
        # Create a target text box
        self.tgt_box = QtWidgets.QTextEdit(self)
        self.tgt_box.setReadOnly(True)
        self.tgt_box.setAcceptRichText(True)
        # Create a middle text box
        self.middle_box = QtWidgets.QTextEdit(self)
        self.middle_box.setAcceptRichText(True)
        # Create a source text box
        self.src_box = QtWidgets.QTextEdit(self)
        self.src_box.setAcceptRichText(True)
        # Create bottom items
        self.src_lang_box = QtWidgets.QLineEdit(self)
        self.tgt_lang_box = QtWidgets.QLineEdit(self)
        self.middle_lang_box = QtWidgets.QLineEdit(self)
        self.src_lang_box.setFixedWidth(50)
        self.tgt_lang_box.setFixedWidth(50)
        self.middle_lang_box.setFixedWidth(50)
        # show candidate list when clicked
        self.src_lang_box.focusInEvent = lambda _: self._show_candidates(1)
        self.tgt_lang_box.focusInEvent = lambda _: self._show_candidates(2)
        self.middle_lang_box.focusInEvent = lambda _: self._show_candidates(3)
        self.trans_btn = QtWidgets.QPushButton("Translate", self)
        self.trans_btn.clicked.connect(lambda: self.translate())
        self.toggle_double_btn = QtWidgets.QPushButton("toggle", self)
        self.toggle_double_btn.clicked.connect(lambda: self.toggle_double())

        # Create a splitter for text box
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.addWidget(self.tgt_box)
        self.splitter.addWidget(self.middle_box)
        self.splitter.addWidget(self.src_box)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setCollapsible(2, False)

        # Create horizontal bottom layout
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.bottom_layout.addWidget(self.src_lang_box)
        self.bottom_layout.addWidget(self.middle_lang_box)
        self.bottom_layout.addWidget(self.tgt_lang_box)
        self.bottom_layout.addWidget(self.trans_btn)
        self.bottom_layout.addWidget(self.toggle_double_btn)
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
        elif self.box_selected is 3:
            logger.debug("intermediate_lang -> " + lang)
            self.middle_lang_box.setText(lang)
            self.cand_list.hide()

    def _set_langs(self, src_lang, tgt_lang, middle_lang):
        self.src_lang_box.setText(src_lang)
        self.tgt_lang_box.setText(tgt_lang)
        self.middle_lang_box.setText(middle_lang)

    def _get_langs(self):
        src_lang = self.src_lang_box.text()
        tgt_lang = self.tgt_lang_box.text()
        middle_lang = self.middle_lang_box.text()
        return src_lang, tgt_lang, middle_lang

    def translate(self, src_text=None):
        if src_text is None:
            # Fetch source text from GUI
            logger.debug('Translate the text in tgt_box')
            src_text = self.src_box.toPlainText()
        else:
            # Set passed source text to GUI
            logger.debug('Translate the passed text')
            src_text = src_text.replace("　", " ")
            self.src_box.setHtml(src_text)

        if self.is_double:
            middle_text = self.middle_box.toPlainText()
            src_lang, tgt_lang, middle_lang = self._get_langs()
            if src_text == '':
                logger.debug('Skip empty text')
                return

            # Check previous status
            if src_text != self.prev_src_text or \
               src_lang != self.prev_src_lang or \
               middle_lang != self.prev_middle_lang:
                middle_text = gtrans_search(src_lang, middle_lang, src_text)
            else:
                logger.debug('Skip source->intermediate')
            if middle_text != self.prev_middle_text or \
               tgt_text != self.prev_tgt_text or \
               tgt_lang != self.prev_tgt_lang:
                tgt_text = gtrans_search(middle_lang, tgt_lang, middle_text)
            else:
                logger.debug('Skip intermediate->target')

            self.prev_src_text, self.prev_src_lang, \
                self.prev_middle_lang, self.prev_tgt_lang = \
                src_text, src_lang, middle_lang, tgt_lang
            # Set target text to GUI
            self.middle_box.setHtml(middle_text)
        else:
            src_lang, tgt_lang, _ = self._get_langs()
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
        logger.debug('Finish to translate')

    def toggle_double(self):
        if self.is_double:
            self.middle_box.hide()
        else:
            self.middle_box.show()
        self._init_memory()
        self.is_double = not self.is_double
