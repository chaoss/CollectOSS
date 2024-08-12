from functools import wraps
from threading import RLock

def synchronized(func):
    lock = RLock()
    @wraps(func)
    def call_sync(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    return call_sync

class CallbackCollection:
    def __init__(self, **cbs) -> None:
        for name, cb in cbs.items():
            if not callable(cb):
                raise TypeError("A callback must be callable")
            setattr(self, name, cb)
    
    def register(self, name, cb):
        if not callable(cb):
            raise TypeError("A callback must be callable")
        setattr(self, name, cb)
    
    def register_all(self, **cbs):
        for name, cb in cbs.items():
            if not callable(cb):
                raise TypeError("A callback must be callable")
            setattr(self, name, cb)

class UniversalPlaceholder:
    def __getattr__(self, name, default=...):
        return self
    
    def __call__(self, *args, **kwargs):
        pass
