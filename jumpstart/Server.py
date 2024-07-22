import socket
import threading
from pathlib import Path

from .Logging import console
from .utils import synchronized
from .Client import JumpstartClient as Client

class JumpstartServer:
    def __init__(self, socketfile = Path("jumpstart.sock").resolve(), input_lock = threading.Lock()):
        try:
            socketfile.unlink(True)
        except:
            console.critical(f"socket in use: {socketfile}")
            exit(1)
            
        self.socketfile = socketfile
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(socketfile))
        self.server.setblocking(True)
        self.lock = input_lock
        
        self.clients: list[Client] = []
        self.messages = []
        
        self.loop = threading.Thread(target=self.accept_loop, name="console")
        
    def accept_loop(self):
        self.server.listen()
        
        try:
            while request := self.server.accept():
                conn, addr = request
                console.info(f"Accepted client: {len(self.clients)}")
                self.clients.append(Client(conn, self.lock, len(self.clients), destroy_callback = self._remove_client))
        except OSError:
            # OSError is thrown when the socket is closed while blocking on accept
            console.info("Server no longer accepting connections")
        except Exception as e:
            console.error("An exception occurred during accept")
            console.error(str(e))
    
    @synchronized
    def _remove_client(self, client):
        self.clients.remove(client)
    
    def start(self):
        self.loop.start()
    
    def close(self):
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        self.socketfile.unlink()
        
        for client in self.clients:
            client.close(reason="Server shutting down")
