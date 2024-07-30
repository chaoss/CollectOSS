import socket
import threading
from pathlib import Path

from .Logging import console
from .Client import JumpstartClient as Client
from .utils import synchronized, CallbackCollection

class JumpstartServer:
    def __init__(self, callbacks: CallbackCollection,
                 socketfile = Path("jumpstart.sock").resolve(),
                 input_lock = threading.Lock()):
        try:
            socketfile.unlink(True)
        except:
            console.critical(f"socket in use: {socketfile}")
            exit(1)
            
        callbacks.register_all(disconnect=self._remove_client)
            
        self.socketfile = socketfile
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(socketfile))
        self.server.setblocking(True)
        self.lock = input_lock
        callbacks.register("shutdown", self._shutdown_callback)
        self.callbacks = callbacks
        
        self.clients: list[Client] = []
        self.messages = []
        
        self.loop = threading.Thread(target=self.accept_loop, name="console")
        
    def accept_loop(self):
        self.server.listen()
        
        try:
            while request := self.server.accept():
                conn, addr = request
                console.info(f"Accepted client: {len(self.clients)}")
                self.clients.append(Client(conn, self.lock, len(self.clients), callbacks=self.callbacks))
        except OSError:
            # OSError is thrown when the socket is closed while blocking on accept
            console.info("Server no longer accepting connections")
        except Exception as e:
            console.error("An exception occurred during accept")
            console.error(str(e))
    
    @synchronized
    def _remove_client(self, client):
        self.clients.remove(client)
    
    @synchronized
    def _shutdown_callback(self, client):
        console.info("Server shutdown requested")
        self.close()
    
    def start(self):
        self.loop.start()
        
    def closed(self):
        return not self.loop.is_alive()
    
    def close(self):
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        self.socketfile.unlink()
        
        for client in self.clients:
            client.close(reason="Server shutting down")
