# -*- coding: utf-8 -*-

import urllib.parse as urllib_parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class GTransWeb(object):

    def __init__(self, browser_modes=['chrome', 'firefox'], headless=True):
        # Create browser
        self._browser = _create_any_browser(browser_modes, headless)

    def __del__(self):
        if self._browser:
            # Close browser
            try:
                self._browser.quit()
            except ImportError:
                pass  # Escape ImportError in __del__() of Python3.

    def translate(self, src_lang, tgt_lang, src_text, timeout=100):
        ''' Translate via Google website '''

        RES_XPATH = '/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/' + \
                    'div[2]/div[2]/div[1]/div[2]/div/span[1]'

        # Remove previous text
        url = 'https://translate.google.com/#view=home&op=translate'
        self._browser.get(url)

        # Wait for removing previous result
        try:
            WebDriverWait(self._browser, timeout).until(
                    EC.invisibility_of_element_located((By.XPATH, RES_XPATH)))
        except TimeoutException:
            pass

        # Encode for URL
        src_text = urllib_parse.quote_plus(src_text.encode('utf-8'))

        # Open translation URL
        url = 'https://translate.google.com/#view=home&op=translate&' + \
              f'sl={src_lang}&tl={tgt_lang}&text={src_text}'
        self._browser.get(url)

        # Extract result by XPath
        try:
            result_elem = WebDriverWait(self._browser, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, RES_XPATH)))
            tgt_text = result_elem.text
            return tgt_text

        except TimeoutException:
            logger.warn('Timeout to translate')
            return ''


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
