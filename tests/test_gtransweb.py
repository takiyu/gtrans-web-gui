# -*- coding: utf-8 -*-
import unittest

from threading import Event

from gtransweb import log_initializer
from gtransweb import GTransWeb, GTransWebAsync
from gtransweb.gtransweb import _create_browser, _create_any_browser

# logging (root)
from logging import getLogger, DEBUG
log_initializer.set_root_level(DEBUG)
logger = getLogger(__name__)


class GTransWebTest(unittest.TestCase):

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

    def test_gtransweb(self):
        gtrans = GTransWeb(headless=True)

        tgt_text = gtrans.translate('en', 'ja', 'This is a pen')
        self.assertEqual(tgt_text, 'これはペンです')
        tgt_text = gtrans.translate('en', 'ja', 'This is an apple')
        self.assertEqual(tgt_text, 'これはリンゴです')

        tgt_text = gtrans.translate('ja', 'en', 'これはペンです').lower()
        self.assertEqual(tgt_text, 'this is a pen')
        tgt_text = gtrans.translate('ja', 'en', 'これはリンゴです').lower()
        self.assertEqual(tgt_text, 'this is an apple')

        tgt_text = gtrans.translate('auto', 'ja', 'This is a pen')
        self.assertEqual(tgt_text, 'これはペンです')

        tgt_text = gtrans.translate('auto', 'en', 'これはペンです').lower()
        self.assertEqual(tgt_text, 'this is a pen')

    def test_gtransweb_async_infinite(self):
        gtrans_async = GTransWebAsync(headless=True, queue_size=0)  # Infinite
        self.async_cnt = 0
        self.async_finish = Event()

        def callback(tgt_text):
            if self.async_cnt == 0:
                self.assertEqual(tgt_text, 'これはペンです')
            elif self.async_cnt == 1:
                self.assertEqual(tgt_text, 'これはリンゴです')
            elif self.async_cnt == 2:
                self.assertEqual(tgt_text.lower(), 'this is a pen')
            elif self.async_cnt == 3:
                self.assertEqual(tgt_text.lower(), 'this is an apple')
                self.async_finish.set()
            self.async_cnt += 1

        gtrans_async.set_callback(callback)

        gtrans_async.translate('en', 'ja', 'This is a pen')
        gtrans_async.translate('en', 'ja', 'This is an apple')
        gtrans_async.translate('ja', 'en', 'これはペンです')
        gtrans_async.translate('ja', 'en', 'これはリンゴです')

        self.async_finish.wait()

    def test_gtransweb_async(self):
        gtrans_async = GTransWebAsync(headless=True, queue_size=1)  # only 1
        self.async_cnt = 0
        self.async_finish = Event()

        def callback(tgt_text):
            if self.async_cnt == 0:
                self.assertEqual(tgt_text, 'これはペンです')
            elif self.async_cnt == 1:
                self.assertEqual(tgt_text.lower(), 'this is an apple')
                self.async_finish.set()
            self.async_cnt += 1

        gtrans_async.set_callback(callback)

        gtrans_async.translate('en', 'ja', 'This is a pen')     # Accept
        gtrans_async.translate('en', 'ja', 'This is an apple')  # Ignore
        gtrans_async.translate('ja', 'en', 'これはペンです')    # Ignore
        gtrans_async.translate('ja', 'en', 'これはリンゴです')  # Accept

        self.async_finish.wait()


if __name__ == '__main__':
    unittest.main()
