# -*- coding: utf-8 -*-
import urllib.parse as urllib_parse
from threading import Thread
from queue import Queue, Full, Empty
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())

TOP_URL = 'https://translate.google.com/#view=home&op=translate'
TRA_URL = 'https://translate.google.com/#view=home&op=translate&' + \
          'sl={}&tl={}&text={}'
RES_XPATH = '/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/div[2]/' + \
            'div[1]/div[2]/div/span[1]'


class GTransWeb(object):

    def __init__(self, browser_modes=['chrome', 'firefox'], headless=True):
        # Create browser
        self._browser = _create_any_browser(browser_modes, headless)
        # Open top page
        self._browser.get(TOP_URL)

    def exit(self):
        # Close browser
        if self._browser:
            self._browser.quit()

    def translate(self, src_lang, tgt_lang, src_text, timeout=10):
        ''' Translate via Google website '''

        # Remove previous text
        self._browser.get(TOP_URL)

        # Wait for removing previous result
        try:
            WebDriverWait(self._browser, timeout).until(
                    EC.invisibility_of_element_located((By.XPATH, RES_XPATH)))
        except TimeoutException:
            pass

        # Encode for URL
        src_text = urllib_parse.quote_plus(src_text.encode('utf-8'))

        # Open translation URL
        self._browser.get(TRA_URL.format(src_lang, tgt_lang, src_text))

        # Extract result by XPath
        try:
            result_elem = WebDriverWait(self._browser, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, RES_XPATH)))
            tgt_text = result_elem.text
            return tgt_text

        except TimeoutException:
            logger.warn('Timeout to translate')
            return ''


class GTransWebAsync(object):
    def __init__(self, browser_modes=['chrome', 'firefox'], headless=True,
                 queue_size=1, query_interval=0.05):
        self._gtransweb = GTransWeb(browser_modes, headless)

        self._query_queue = Queue(maxsize=queue_size)
        self._query_interval = query_interval
        self._thread = Thread(target=self._trans_loop, daemon=True)
        self._callback = None

        self._thread.start()

    def exit(self):
        # Close browser
        self._gtransweb.exit()

    def set_callback(self, callback):
        ''' Set callback which is call when translation is finished
            :param callback: Callback function. It must perform
                             `callback(tgt_text)` and it called in another
                             thread asynchronously.
        '''
        self._callback = callback

    def translate(self, src_lang, tgt_lang, src_text, timeout=10):
        query = (src_lang, tgt_lang, src_text, timeout)
        while True:
            try:
                # Push new item
                self._query_queue.put_nowait(query)
                # Success
                return
            except Full:
                # Pop oldest item
                try:
                    time.sleep(self._query_interval)
                    self._query_queue.get_nowait()
                except Empty:
                    pass

    def _trans_loop(self):
        while True:
            # Wait for query
            query = self._query_queue.get()

            # Translate
            tgt_text = self._gtransweb.translate(*query)

            # Pass the result
            if callable(self._callback):
                self._callback(tgt_text)
            else:
                logger.error('Callback is not set')


def _create_browser(mode, headless=True):
    ''' Create a browser instance '''
    logger.debug(f'Create browser (mode: {mode}, headless: {headless}')
    try:
        if mode == 'chrome':
            # Chrome
            from selenium.webdriver import Chrome, ChromeOptions
            options = ChromeOptions()
            if headless:
                options.add_argument('--headless')
            return Chrome(options=options)

        elif mode == 'firefox':
            # Firefox
            from selenium.webdriver import Firefox, FirefoxOptions
            options = FirefoxOptions()
            if headless:
                options.add_argument('-headless')
            return Firefox(options=options, service_log_path=None)

        else:
            logger.error('Unknown browser mode')
            return None

    except Exception:
        logger.error('Failed to create browser')
        return None


def _create_any_browser(modes, headless):
    ''' Create an available browser instance by trying to create '''
    logger.debug('Create any browser')

    for mode in modes:
        # Try to create browser
        browser = _create_browser(mode, headless)
        if browser is None:
            continue  # Failed
        else:
            return browser  # Found

    logger.error('No browser is valid')
    return None
