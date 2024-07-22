import json
import socket
import threading

from .Logging import console
from .utils import synchronized
from .API import spec, Status, Command

class JumpstartClient:
    def __init__(self, sock: socket.socket, wake_lock: threading.Lock, ID: int, destroy_callback):
        self.socket = sock
        self.io = socket.SocketIO(sock, "rw")
        self.lock = wake_lock
        self.ID = ID
        self.respond(spec)
        self.thread = threading.Thread(target=self.loop, args=[destroy_callback], name=f"client_{ID}")
        self.thread.start()
    
    def loop(self, callback):
        while line := self.io.readline().decode():
            console.info(f"Recieved message: {line}")
            
            try:
                body = json.loads(line)
                console.info(body)
            except json.JSONDecodeError:
                self.send(Status.error("Invalid JSON"))
        
        console.info(f"Client disconnect")
        callback(self)
    
    @synchronized
    def send(self, *args, **kwargs):
        if args and kwargs:
            kwargs["args"] = args
        
        if self.io.closed:
            return
        
        self.io.write((json.dumps(kwargs) + "\n").encode())
        self.io.flush()
    
    @synchronized
    def respond(self, msg: Status):
        if self.io.closed:
            return
        
        self.io.write((json.dumps(msg) + "\n").encode())
        self.io.flush()
    
    @synchronized
    def close(self, **kwargs):
        self.send(status="T", **kwargs)
        self.io.close()
        self.thread.join()
