# -*- coding: utf-8 -*-
from contextlib import contextmanager
from tornado.locks import Lock


class SessionManager(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = Lock()
        self._session_locks = {}

    @contextmanager
    def get(self, key):
        try:
            self._lock.acquire()
            if key not in self:
                self._session_locks[key] = Lock()
                self[key] = {}
        finally:
            self._lock.release()

        try:
            self._session_locks[key].acquire()
            yield self[key]
        finally:
            self._session_locks[key].release()
