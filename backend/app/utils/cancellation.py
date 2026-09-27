"""Cooperative cancellation: an in-flight provider request cannot be interrupted."""
import threading
import time


class OperationCancelled(Exception):
    pass


class CancellationToken:
    def __init__(self, parent=None, timeout=None):
        self._event = threading.Event()
        self.parent = parent
        self.deadline = time.monotonic() + timeout if timeout is not None else None

    def cancel(self):
        self._event.set()

    def is_cancelled(self):
        return (self._event.is_set() or
                (self.parent is not None and self.parent.is_cancelled()) or
                (self.deadline is not None and time.monotonic() >= self.deadline))

    def check(self):
        if self.is_cancelled():
            raise OperationCancelled('Operation cancelled')


def check_cancelled(token):
    if token is not None:
        token.check()
