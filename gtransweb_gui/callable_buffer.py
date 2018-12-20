# -*- coding: utf-8 -*-
from collections import deque
from threading import Timer
import time

from PyQt5 import QtCore

# logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class CallableBuffer(object):
    def __init__(self):
        self._query = None  # Only newest one
        self._timer = False

        self._buftime = 0.5

    def get_buftime(self):
        ''' Get buffering time (sec) '''
        return self._buftime

    def set_buftime(self, buftime):
        ''' Set buffering time (sec) '''
        self._buftime = buftime

    def __call__(self, callback, *args, **kwargs):
        # Overwrite by new query
        self._query = (callback, args, kwargs)

        # Start new timer
        if not self._timer:
            self._timer = True
            QtCore.QTimer.singleShot(self._buftime * 1000, self._postcall)
            # self._timer = Timer(self._buftime, self._postcall)
            # self._timer.start()

    def _postcall(self):
        # Timer is finished
        self._timer = False

        # Decompose query
        callback, args, kwargs = self._query

        # Check callback function
        if not callable(callback):
            logger.error('Callback is not set')
            return

        # Call
        callback(*args, **kwargs)
