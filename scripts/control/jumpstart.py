import os
import sys
import time
import json
import socket
import signal
import logging
import threading
from pathlib import Path

# Preemt globals declared later in scope
# Purely performative
globals().update({
    "messages": None,
    "console": None,
    "clients": None,
    "server": None
})

def init_logging(console = logging.Logger("jumpstart") , errlog_file = Path("logs/jumpstart.error"), stdout_file = Path("logs/jumpstart.log")) -> logging.Logger:
    errlog = logging.FileHandler(errlog_file, "w")
    stdout = logging.FileHandler(stdout_file, "w")

    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(process)d]->[%(threadName)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S %z")

    errlog.setLevel(logging.WARN)
    stdout.setLevel(logging.INFO)
    stdout.addFilter(lambda entry: entry.levelno < logging.WARN)
    errlog.formatter = stdout.formatter = formatter

    console.addHandler(errlog)
    console.addHandler(stdout)
    console.setLevel(logging.INFO)

def handle_terminate(*args, **kwargs):
    console.info("shutting down")
    
    global server, socketfile, clients
    
    for client in clients:
        client.close()

    server.close()
    socketfile.unlink()
    
    exit(0)

def input_loop(wake_lock: threading.Lock, server: socket.socket):
    server.listen()
    global clients, messages
    clients = []
    messages = []
    
    while True:
        conn, addr = server.accept()
        console.info(f"Accepted client: {addr}")
        clients.append(Client(conn, wake_lock, len(clients)))
        
    server.close()

class Client:
    def __init__(self, sock: socket.socket, wake_lock: threading.Lock, ID: int):
        self.socket = sock
        sock.setblocking(True)
        self.io = socket.SocketIO(sock, "rw")
        self.lock = wake_lock
        self.ID = ID
        self.thread = threading.Thread(target=self.loop, args=[self])
    
    def loop(self):
        global console
        
        while line := self.io.readline().decode():
            console.info(f"Recieved message: {line}")
            
            try:
                body = json.loads(line)
            except json.JSONDecodeError:
                self.io.write(json.dumps({
                    "status": "E",
                    "detail": "Invalid JSON"
                }) + "\n")
        
        console.info(f"Client disconnect: {self.ID}")
    
    def close(self):
        self.io.close()

if __name__ == "__main__":
    global console
    console = init_logging()
    
    global socketfile
    socketfile = Path("jumpstart.sock").resolve()
    
    try:
        socketfile.unlink(True)
    except:
        console.critical(f"socket in use: {socketfile}")
        exit(1)
    
    global server
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(socketfile))
    server.setblocking(True)
    
    signal.signal(signal.SIGTERM, handle_terminate)
    signal.signal(signal.SIGINT, handle_terminate)
    threading.current_thread().setName("main")
    input_lock = threading.Lock()

    loop = threading.Thread(target=input_loop, args=[input_lock, server])
    loop.setName("console")
    loop.start()
    
    while True:
        if input_lock.acquire(True, 1):
            # The input thread has notified us of a new message
            pass
        else:
            pass