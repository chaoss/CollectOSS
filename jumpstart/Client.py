import json
import socket
import threading

from .Logging import console
from .API import spec, Status, Command
from .utils import synchronized, CallbackCollection

class JumpstartClient:
    def __init__(self, sock: socket.socket, wake_lock: threading.Lock, ID: int, callbacks: CallbackCollection):
        self.socket = sock
        self.io = socket.SocketIO(sock, "rw")
        self.lock = wake_lock
        self.ID = ID
        self.respond(spec)
        self.thread = threading.Thread(target=self.loop,
                                       args=[callbacks],
                                       name=f"client_{ID}")
        self.thread.start()
    
    def loop(self, cbs):
        while line := self.io.readline().decode():
            try:
                body = json.loads(line)
                
                if not "cmd" in body:
                    self.respond(Status.error("Command unspecified"))
                
                cmd = Command.of(body)
                if cmd == Command.status:
                    status_dict = cbs.status()
                    self.respond(Status.status(status_dict))
                if cmd == Command.shutdown:
                    cbs.shutdown(self)
                if cmd == Command.start:
                    cbs.start(body["component"], self, *body.get("options", []))
                if cmd == Command.stop:
                    cbs.stop(body["component"], self)
            except json.JSONDecodeError:
                self.respone(Status.error("Invalid JSON"))
            except Exception as e:
                self.respond(Status.error(str(e)))
                console.exception("Exception while handling request: " + line)
        
        console.info(f"Disconnect")
        cbs.disconnect(self)
    
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
        # console.info(msg)
        self.io.write((json.dumps(msg) + "\n").encode())
        self.io.flush()
    
    @synchronized
    def close(self, **kwargs):
        self.send(status="T", **kwargs)
        self.io.close()
        
        if not self.thread is threading.currentThread():
            self.thread.join()
