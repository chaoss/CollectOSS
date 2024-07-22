from functools import wraps
from threading import Lock

def synchronized(func):
    lock = Lock()
    @wraps(func)
    def call_sync(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    return call_sync