# -*- coding: utf-8 -*-
import urllib.parse as urllib_parse
from threading import Thread
from queue import Queue, Full, Empty
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


DEFAULT_BROWSER_MODES = ['chrome', 'firefox']

TOP_URLS = {'google': 'https://translate.google.com/#view=home&op=translate',
            'deepl':  'https://www.deepl.com/translator'}
TRA_URLS = {'google': 'https://translate.google.com/#view=home&op=translate' +
                      '&sl={src_lang}&tl={tgt_lang}&text={src_text}',
            'deepl':  'https://www.deepl.com/translator' +
                      '#{src_lang}/{tgt_lang}/{src_text}'}
RES_XPATHS = {'google': '/html/body/div[2]/div[2]/div[1]/div[2]/div[1]' +
                        '/div[1]/div[2]/div[3]/div[1]/div[2]/div/span[1]/span',
              'deepl': '/html/body/div[2]/div[1]/div[1]/div[4]/div[3]/div[2]' +
                       '/p[1]/button[1][text()!=""]'}


class GTransWeb:
    BACKEND_MODES = ['google', 'deepl']

    def __init__(self, backend_mode='google',
                 browser_modes=DEFAULT_BROWSER_MODES, headless=True,
                 timeout=5):
        self._backend_mode = backend_mode
        self._browser_modes = browser_modes
        self._headless = headless
        self._timeout = timeout  # sec

        # Create browser first
        self._create_browser()

    def get_backend_mode(self):
        return self._backend_mode

    def is_headless(self):
        return self._headless

    def _create_browser(self):
        # Close previous browser
        self.exit()
        # Create
        self._browser = _create_any_browser(self._browser_modes,
                                            self._headless)
        # Open top page
        self._browser.get(TOP_URLS[self._backend_mode])

    def exit(self):
        # Try to close browser
        try:
            if self._browser:
                self._browser.quit()
        except Exception:
            pass

    def translate(self, src_lang, tgt_lang, src_text):
        ''' Translate via Google website '''
        while True:
            # Try to translate
            try:
                return self._translate(src_lang, tgt_lang, src_text)
            except WebDriverException:
                # Restart browser
                self._create_browser()
                # Try again

    def _translate(self, src_lang, tgt_lang, src_text):
        if not src_text:
            return ''

        backend_mode = self._backend_mode

        if backend_mode == 'google':
            # Remove previous text
            self._browser.get(TOP_URLS[backend_mode])

            # Wait for removing previous result
            try:
                xpath = RES_XPATHS[backend_mode]
                WebDriverWait(self._browser, self._timeout).until(
                        EC.invisibility_of_element_located((By.XPATH, xpath)))
            except TimeoutException:
                pass

        if backend_mode == 'google':
            # Encode for URL
            src_text = urllib_parse.quote_plus(src_text.encode('utf-8'))

        # Open translation URL
        tra_url = TRA_URLS[backend_mode]
        self._browser.get(tra_url.format(src_lang=src_lang, tgt_lang=tgt_lang,
                                         src_text=src_text))

        # Extract result by XPath
        try:
            xpath = RES_XPATHS[backend_mode]
            result_elem = WebDriverWait(self._browser, self._timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
            if backend_mode == 'google':
                tgt_text = result_elem.text
            else:
                tgt_text = result_elem.get_attribute("innerHTML")
            return tgt_text

        except TimeoutException:
            logger.warn('Timeout to translate')
            return ''


class GTransWebAsync:
    def __init__(self, backend_mode='google',
                 browser_modes=DEFAULT_BROWSER_MODES, headless=True,
                 timeout=5, queue_size=1, query_interval=0.05):
        self._gtransweb = GTransWeb(browser_modes, headless, timeout)

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

    def translate(self, src_lang, tgt_lang, src_text):
        query = (src_lang, tgt_lang, src_text)
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
