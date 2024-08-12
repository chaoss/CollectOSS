import os
import sys
import time
import json
import socket
import signal
import logging
import threading

from pathlib import Path
from subprocess import Popen, PIPE, STDOUT

from .API import Status
from .API import Component
from .Logging import console
from .procman import ProcessManager
from .Server import JumpstartServer
from .utils import CallbackCollection
from .utils import UniversalPlaceholder

global server, manager

def handle_terminate(*args, **kwargs):
    console.info("shutting down")
    
    manager.stop(Component.all, UniversalPlaceholder())
    server.close()
    
    exit(0)
    
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_terminate)
    signal.signal(signal.SIGINT, handle_terminate)
    threading.current_thread().setName("main")
    
    manager = ProcessManager()
    
    callbacks = CallbackCollection(start=manager.start, stop=manager.stop, status=manager.status)
    server = JumpstartServer(callbacks)
    server.start()
    
    while not server.closed():
        try:
            manager.refresh()
        except:
            console.exception("Exception while refreshing status")
            server.broadcast("Exception while refreshing status, going down", Status.error)
            break
        
        if server.lock.acquire(True, 0.1):
            # The input thread has notified us of a new message
            server.lock.release()
            pass
        else:
            time.sleep(0.1)

    handle_terminate()
