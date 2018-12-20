# -*- coding: utf-8 -*-
import unittest

import time
from threading import Event

from gtransweb import log_initializer
from gtransweb_gui.callable_buffer import CallableBuffer

# logging (root)
from logging import getLogger, DEBUG
log_initializer.set_root_level(DEBUG)
logger = getLogger(__name__)


class CallableBufferTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_postpone(self):
        callable_buf = CallableBuffer()

        buffering_finish = Event()

        def callback(n, s):
            self.assertEqual(n, 56)
            self.assertEqual(s, 'ghi')
            buffering_finish.set()

        callable_buf.set_buftime(0.5)

        # Start buffering
        prev_time = time.time()
        callable_buf(callback, 12, s='abc')
        time.sleep(0.1)
        callable_buf(callback, 34, s='def')
        time.sleep(0.1)
        callable_buf(callback, 56, s='ghi')
        buffering_finish.wait()
        post_time = time.time()

        # Elapsed time should be 0.5 sec not 0.7 (0.5 + 0.1 + 0.1).
        self.assertAlmostEqual(post_time - prev_time, 0.5, places=2)


if __name__ == '__main__':
    unittest.main()
