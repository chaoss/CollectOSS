spec = {
    "commands": [
        {
            "name": "status",
            "desc": "Display the current status of Augur processes",
            "args": []
        }, {
            "name": "start",
            "desc": "Start one or more components of Augur",
            "args": [
                {
                    "name": "component",
                    "required": True,
                    "type": "enum",
                    "values": [
                        "all", "frontend", "api", "collection"
                    ]
                }, {
                    "name": "options",
                    "required": False,
                    "type": "list"
                }
            ]
        }, {
            "name": "stop",
            "desc": "Stop one or more components of Augur",
            "args": [
                {
                    "name": "component",
                    "required": True,
                    "type": "enum",
                    "values": [
                        "all", "frontend", "api", "collection"
                    ]
                }
            ]
        }, {
            "name": "restart",
            "desc": "restart one or more components of Augur",
            "args": [
                {
                    "name": "component",
                    "required": True,
                    "type": "enum",
                    "values": [
                        "all", "frontend", "api", "collection"
                    ]
                }
            ]
        }, {
            "name": "shutdown",
            "desc": "Stop all Augur components and shut down Jumpstart",
            "args": []
        }
    ],
    "statuses": [
        {
            "ID": "E",
            "desc": "An error occurred",
            "fields": [
                {
                    "key": "detail",
                    "desc": "A detail message about the error",
                    "required": True
                }
            ]
        }, {
            "ID": "T",
            "desc": "Connection terminated",
            "fields": [
                {
                    "key": "reason",
                    "desc": "A message describing the reason for disconnection",
                    "required": False
                }
            ]
        }, {
            "ID": "I",
            "desc": "Information from server",
            "fields": [
                {
                    "key": "detail",
                    "desc": "An informational message from the jumpstart server",
                    "required": True
                }
            ]
        }, {
            "ID": "S",
            "desc": "Status of Augur components",
            "fields": [
                {
                    "key": "frontend",
                    "desc": "The frontend status",
                    "required": True
                }, {
                    "key": "api",
                    "desc": "The API status",
                    "required": True
                }, {
                    "key": "collection",
                    "desc": "The collection status",
                    "required": True
                }
            ]
        }
    ]
}

from enum import Enum, auto

class Status(Enum):
    error="E"
    terminated="T"
    information="I"
    status="S"
    
    @classmethod
    def __call__(self, msg = None):
        if self == Status.error:
            return {
                "status": self.value,
                "detail": msg or "unspecified"
            }
        elif self == Status.success:
            return {
                "status": self.value
            }
        elif self == Status.terminated:
            if not msg:
                return {
                    "status": self.value
                }
            else:
                return {
                    "status": self.value,
                    "reason": msg
                }
        elif self == Status.information:
            return {
                "status": self.value,
                "detail": msg or "ack"
            }
        elif self == Status.status:
            return {
                "status": self.value,
                "frontend": None,
                "api": None,
                "collection": None
            }

class Command(Enum):
    status=auto()
    start=auto()
    stop=auto()
    restart=auto()
    shutdown=auto()
    unknown=auto()
    
    @staticmethod
    def of(msg: dict):
        if msg["name"] == "status":
            msg.pop("name")
            return Command.status(msg)
    
    @classmethod
    def __call__(self, args):
        self.args = args
        return self
    
Component = Enum("Component", ["all", "frontend", "api", "collection"])