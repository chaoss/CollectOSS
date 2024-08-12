from .API import Status
from .API import Component
from .Logging import console
from .utils import synchronized
from .utils import UniversalPlaceholder
from .Client import JumpstartClient as Client

import signal

from time import sleep
from typing import Union
from pathlib import Path
from threading import Lock
from subprocess import Popen, PIPE, STDOUT, run

class ProcessManager:
    def __init__(self):
        self.frontend = False
        self._frontend = None
        self.collection = False
        self._collection = None
        
        # Ensure a read of the component status cannot happen during bringup
        self._startlock = Lock()
        
        self.frontend_stdout = Path("logs/jumpstart_frontend.info")
        self.frontend_stderr = Path("logs/jumpstart_frontend.error")
        self.collection_stdout = Path("logs/jumpstart_collection.info")
        self.collection_stderr = Path("logs/jumpstart_collection.error")
    
    def status(self):
        return {
            "frontend": self.frontend,
            "api": self.frontend,
            "collection": self.collection
        }
    
    @synchronized
    def start(self, component: Union[Component, str], client: Client, *options):
        if not (c := Component.from_str(component)):
            client.respond(Status.error(f"Invalid component for start: {component}"))
            return
        
        if c in (Component.api, Component.frontend, Component.all):
            if self.frontend:
                client.respond(Status.information(f"The frontend/api is already running"))
            else:
                with(self._startlock):
                    self._frontend = {
                        "stdout": self.frontend_stdout.open("w"),
                        "stderr": self.frontend_stderr.open("w")
                    }
                    self._frontend["process"] = Popen("augur api start".split() + list(options),
                                        stdout=self._frontend["stdout"],
                                        stderr=self._frontend["stderr"])
        if c in (Component.collection, Component.all):
            if self.collection:
                client.respond(Status.information(f"The collection is already running"))
            else:
                with(self._startlock):
                    self._collection = {
                        "stdout": self.collection_stdout.open("w"),
                        "stderr": self.collection_stderr.open("w")
                    }
                    self._collection["process"] = Popen("augur collection start".split() + list(options),
                                            stdout=self._collection["stdout"],
                                            stderr=self._collection["stderr"])
    
    @synchronized
    def stop(self, component: Union[Component, str], client: Client):
        if not (c := Component.from_str(component)):
            client.respond(Status.error(f"Invalid component for stop: {component}"))
            return
        
        if c in (Component.api, Component.frontend, Component.all):
            if not self.frontend:
                client.respond(Status.information("The frontend/api is not running"))
            else:
                self._frontend["process"].send_signal(signal.SIGINT)
                run("augur api stop".split(), stderr=PIPE, stdout=PIPE)
        if c in (Component.collection, Component.all):
            if not self.collection:
                client.respond(Status.information("The collection is not running"))
            else:
                self._collection["process"].send_signal(signal.SIGINT)
                run("augur collection stop".split(), stderr=PIPE, stdout=PIPE)
    
    @synchronized
    def shutdown(self):
        self.stop(Component.all, UniversalPlaceholder())
        
        while self.refresh():
            sleep(0.1)
        
    @synchronized
    def refresh(self):
        with(self._startlock):
            if self._frontend is not None:
                if self._frontend["process"].poll() is not None:
                    self.frontend = False
                    self._frontend["stderr"].close()
                    self._frontend["stdout"].close()
                    self._frontend = None
                    console.info("Frontend shut down")
                else:
                    self.frontend = True
            if self._collection is not None:
                if self._collection["process"].poll() is not None:
                    self.collection = False
                    self._collection["stderr"].close()
                    self._collection["stdout"].close()
                    self._collection = None
                    console.info("Collection shut down")
                else:
                    self.collection = True
            
            return self.frontend or self.collection