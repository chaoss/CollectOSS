from enum import Enum, EnumMeta, auto

Component = Enum("Component", ["all", "frontend", "api", "collection"])

class Status(Enum):
    error="E"
    terminated="T"
    information="I"
    status="S"
    
    def __call__(self, msg = None):
        response = {"status": self.value}
        
        if self == Status.error:
            response.update({
                "detail": msg or "unspecified"
            })
        elif self == Status.terminated:
            if msg:
                response.update({
                    "reason": msg
                })
        elif self == Status.information:
            response.update({
                "detail": msg or "ack"
            })
        elif self == Status.status:
            response.update(msg)
        
        return response

class Command(Enum):
    status=auto()
    start=auto()
    stop=auto()
    restart=auto()
    shutdown=auto()
    unknown=auto()
    
    @staticmethod
    def of(msg: dict):
        cmd = msg.pop("cmd")
        
        try:
            return Command[cmd]
        except KeyError:
            raise Exception(f"Unknown command: [{cmd}]")
    
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
                    "type": Component
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
                    "type": Component
                }
            ]
        }, {
            "name": "restart",
            "desc": "restart one or more components of Augur",
            "args": [
                {
                    "name": "component",
                    "required": True,
                    "type": Component
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

for command in spec["commands"]:
    for arg in command["args"]:
        if issubclass(type(arg["type"]), (Enum, EnumMeta)):
            t = arg["type"]
            arg["type"] = "enum"
            arg["values"] = [c.name for c in t]
