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

global server

def handle_terminate(*args, **kwargs):
    console.info("shutting down")
    
    server.close()
    
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_terminate)
    signal.signal(signal.SIGINT, handle_terminate)
    threading.current_thread().setName("main")
    
    server = JumpstartServer()
    server.start()
    
    while True:
        if server.lock.acquire(True, 0.1):
            # The input thread has notified us of a new message
            server.lock.release()
            pass
        else:
            time.sleep(0.1)
