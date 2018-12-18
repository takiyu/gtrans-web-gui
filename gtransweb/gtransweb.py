# -*- coding: utf-8 -*-


import urllib.parse as urllib_parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


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


class GTransWeb(object):
    def __init__(self, browser_modes=['chrome', 'firefox'], headless=True):
        # Create browser
        self._browser = _create_any_browser(browser_modes, headless)

    def __del__(self):
        # Close browser
        if self._browser:
            self._browser.quit()

    def translate(self, src_lang, tgt_lang, src_text, timeout=5):
        ''' Translate via Google website '''

        # Encode for URL
        src_text = urllib_parse.quote_plus(src_text.encode('utf-8'))

        # Create URL
        url = 'https://translate.google.com/#view=home&op=translate&' + \
              f'sl={src_lang}&tl={tgt_lang}&text={src_text}'

        # Open
        self._browser.get(url)

        # Extract result by XPath
        xpath = '/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/' + \
                'div[2]/div[1]/div[2]/div/span[1]/span'
        try:
            result_elem = WebDriverWait(self._browser, timeout).until(
                    EC.visibility_of_element_located((By.XPATH, xpath)))
            tgt_text = result_elem.text
            return tgt_text

        except TimeoutException:
            logger.warn('Timeout to translate')
            return ''
