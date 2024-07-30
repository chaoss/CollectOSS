import os
import sys
import time
import json
import socket
import signal
import logging
import threading
from pathlib import Path

from .Logging import console
from .Server import JumpstartServer
from .utils import synchronized, CallbackCollection

global server

def handle_terminate(*args, **kwargs):
    console.info("shutting down")
    
    server.close()
    
    exit(0)

frontend = False
collection = False

@synchronized
def start_component(component) -> bool:
    """Returns True if the given component was not already running"""

@synchronized
def stop_component(component) -> bool:
    """Returns True if the given component was running and was stopped"""

@synchronized
def get_status():
    return {
        "frontend": frontend,
        "api": frontend,
        "collection": bool(collection)
    }
    
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_terminate)
    signal.signal(signal.SIGINT, handle_terminate)
    threading.current_thread().setName("main")
    
    callbacks = CallbackCollection(start=start_component, stop=stop_component, status=get_status)
    server = JumpstartServer(callbacks)
    server.start()
    
    while not server.closed():
        if server.lock.acquire(True, 0.1):
            # The input thread has notified us of a new message
            server.lock.release()
            pass
        else:
            time.sleep(0.1)
