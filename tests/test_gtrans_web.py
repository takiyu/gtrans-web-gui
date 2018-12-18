# -*- coding: utf-8 -*-
import unittest

from gtransweb import log_initializer
from gtransweb import GTransWeb
from gtransweb.gtransweb import _create_browser, _create_any_browser

# logging (root)
from logging import getLogger, DEBUG
log_initializer.set_root_level(DEBUG)
logger = getLogger(__name__)


class GtransWebTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_browser(self):
        browser = _create_browser('chrome', headless=True)
        self.assertIsNotNone(browser)
        browser.quit()

        browser = _create_browser('firefox', headless=True)
        self.assertIsNotNone(browser)
        browser.quit()

        # browser = _create_browser('chrome', headless=False)
        # self.assertIsNotNone(browser)
        # browser.quit()

        # browser = _create_browser('firefox', headless=False)
        # self.assertIsNotNone(browser)
        # browser.quit()

    def test_create_any_browser(self):
        browser = _create_any_browser(['chrome', 'firefox'], headless=True)
        self.assertIsNotNone(browser)
        browser.quit()

    def test_gtrans_web(self):
        gtrans = GTransWeb(headless=True)

        tgt_text = gtrans.translate('en', 'ja', 'This is a pen')
        self.assertEqual(tgt_text, 'これはペンです')

        tgt_text = gtrans.translate('ja', 'en', 'これはペンです')
        self.assertEqual(tgt_text, 'this is a pen')

        tgt_text = gtrans.translate('auto', 'ja', 'This is a pen')
        self.assertEqual(tgt_text, 'これはペンです')

        tgt_text = gtrans.translate('auto', 'en', 'これはペンです')
        self.assertEqual(tgt_text, 'this is a pen')


if __name__ == '__main__':
    unittest.main()
