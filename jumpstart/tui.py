import socket as sockets
from socket import socket

import json
import asyncio
import logging
from sys import argv
from pathlib import Path
from datetime import datetime

from textual import work
from textual.app import App, on
from textual.binding import Binding
from textual.message import Message
from textual.events import Load, Mount
from textual.containers import Horizontal, Vertical
from textual.widgets import RichLog, Input, Button, Label

class JumpstartTUI(App):
    # Setup
    CSS_PATH = "tui.tcss"
    
    """
        The name of a binding's action automatically links
        to a function of the same name, but prefixed with
        "action_". So, by putting "kb_exit" here, I'm
        telling the runtime to call a function named
        "action_kb_exit" any time the user presses CTRL+D.
        
        I don't personally like that, but you'll find the
        function defined below.
    """
    BINDINGS = [
        Binding("ctrl+d", "kb_exit", "Exit", priority=True)
    ]
        
    def compose(self):
        # Yield the app's components on load
        with Horizontal():
            with Vertical(classes="sidebar"):
                with Vertical(classes="status_container"):
                    with Horizontal(classes="info_container"):
                        yield Label("Frontend")
                        yield Label(id="frontend_label", classes="status_label")
                    with Horizontal(classes="info_container"):
                        yield Label("API")
                        yield Label(id="api_label", classes="status_label")
                    with Horizontal(classes="info_container"):
                        yield Label("Collection")
                        yield Label(id="collection_label", classes="status_label")
                        
                yield Button("Status", id="statusbtn")
                yield Button("Exit", variant="error", id="exitbtn")
            
            with Vertical():
                yield RichLog(
                    highlight=True, 
                    auto_scroll=True, 
                    wrap=True,
                    id="stdout"
                )
                yield Input(
                    placeholder="Enter Command",
                    id="command_line",
                    valid_empty=False
                )
    
    class ServerMessage(Message):
        """Add a message to the outgoing queue"""
        
        def __init__(self, **msg) -> None:
            self.msg = msg
            super().__init__()
    
    class DirtyExit(Message):
        """Custom event to shut down app without immediately closing"""
        
        def __init__(self) -> None:
            super().__init__()
    
    class Info(Message):
        """Custom event to print an info message"""
        
        def __init__(self, msg) -> None:
            self.msg = msg
            super().__init__()
        
        def __str__(self):
            return self.msg
    
    class Error(Message):
        """Custom event to print an error message"""
        
        def __init__(self, msg) -> None:
            self.msg = msg
            super().__init__()
        
        def __str__(self):
            return self.msg
    
    class Status(Message):
        """Notify the UI of an updated status"""
        
        def __init__(self, frontend: bool, api: bool, collection: bool):
            self.f = frontend
            self.a = api
            self.c = collection
            super().__init__()
    
    def action_kb_exit(self, force = False):
        """Called when the user requests to exit"""
        inbox = self.query(Input).filter("#command_line").only_one()
        value = inbox.value
        
        if not value or force:
            self.server.shutdown(sockets.SHUT_RDWR)
            self.server_IO.close()
            self.app.exit()
    
    # Logging
    @on(Error)
    def error(self, msg):
        self.out("ERROR", msg)
    
    @on(Info)
    def info(self, msg):
        self.out("INFO", msg)
        
    def out(self, level, msg, source = "console"):
        time_str = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        formatted = "[{}] [{}] [{}] {}".format(time_str, source, level, str(msg))
        self.raw(formatted)
    
    def raw(self, obj, disable_highlighting = False, enable_markup = False):
        stdout = self.query_one(RichLog)
        if disable_highlighting:
            stdout.highlight = False
        if enable_markup:
            stdout.markup = True
        stdout.write(obj)
        if disable_highlighting:
            stdout.highlight = True
        if enable_markup:
            stdout.markup = False
    
    def show_help(self, command = None, *args):
        if not command:
            self.raw(self.help_str, True, True)
        else:
            self.info("Granular help not currently available")
    
    # Events
    @on(Mount)
    async def startup_process_tasks(self):
        # Make sure the cmd input takes focus
        inbox = self.query(Input).filter("#command_line").only_one()
        inbox.focus()
        
        self.server_rec()
        self.status_ping()
    
    @on(DirtyExit)
    def exit_dirty(self):
        self.workers.cancel_all()
        inbox = self.query(Input).filter("#command_line").only_one()
        inbox.value = ""
        inbox.disabled = True
        
        for btn in self.query(Button).results():
            if not btn.id == "exitbtn":
                btn.disabled = True
        
        self.error("Use CTRL+D or CTRL+C to exit")
    
    @on(Button.Pressed, "#exitbtn")
    def handle_btn_exit(self):
        self.action_kb_exit(True)
    
    @on(Input.Submitted, "#command_line")
    def accept_input(self, event: Input.Submitted):
        value = event.value
        
        # The input box only accepts non-empty strings
        cmd, *args = value.split()
        
        if cmd == "exit":
            self.action_kb_exit(True)
        
        self.out("INFO", value, "user")
        event.input.value = ""
        
        if cmd == "help":
            self.show_help(*args)
            
        packet = {}
            
        for command in self.spec["commands"]:
            if command["name"] == cmd:
                packet["cmd"] = cmd
                for arg in command["args"]:
                    if arg["required"] and not len(args):
                        self.error(f'Missing required positional argument: [{arg["name"]}]')
                        return
                    elif len(args):
                        if arg["type"] == "enum":
                            if args[0] not in arg["values"]:
                                self.error(f'Invalid value for arg [{arg["name"]}]')
                                self.error(f'> Must be one of <{", ".join(arg["values"])}>')
                                return
                            packet[arg["name"]] = args.pop(0)
                        elif arg["type"] == "list":
                            packet[arg["name"]] = args
                            break
                break
        if packet:
            self.send(**packet)
        else:
            self.error("Unknown command")
        

    @on(Button.Pressed, "#statusbtn")
    def get_status(self):
        self.send(cmd = "status")
    
    @on(ServerMessage)
    def server_send(self, carrier: ServerMessage):
        self.send(**carrier.msg)
        
    @on(Status)
    def status_update(self, status):
        labels = self.query(".status_label")
        
        for label in labels:
            if label.id == "frontend_label":
                if status.f:
                    label.add_class("label_up")
                else:
                    label.remove_class("label_up")
            elif label.id == "api_label":
                if status.a:
                    label.add_class("label_up")
                else:
                    label.remove_class("label_up")
            elif label.id == "collection_label":
                if status.c:
                    label.add_class("label_up")
                else:
                    label.remove_class("label_up")
    
    # Server communication
    def send(self, **kwargs):
        try:
            self.server_IO.write((json.dumps(kwargs) + "\n").encode())
            self.server_IO.flush()
        except Exception:
            self.post_message(self.DirtyExit())
    
    def sendraw(self, msg: str):
        self.server_IO.write((msg + "\n").encode())
        self.server_IO.flush()
    
    # Worker tasks
    @work(name="status")
    async def status_ping(self):
        while not hasattr(self, "server_IO"):
            # Wait for server connection
            await asyncio.sleep(0.1)
        
        await asyncio.sleep(1)
            
        while not self.server_IO.closed:
            self.post_message(self.ServerMessage(cmd = "status"))
            await asyncio.sleep(1)
    
    @work(name="server", thread=True)
    def server_rec(self):
        stdout = self.query_one(RichLog)
        
        def log(obj):
            self.call_from_thread(stdout.write, obj)
            
        def info(msg, source = "server"):
            time_str = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
            formatted = "[{}] [{}] [INFO] {}".format(time_str, source, msg)
            log(formatted)
            
        def error(msg, source = "server"):
            time_str = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
            formatted = "[{}] [{}] [ERROR] {}".format(time_str, source, msg)
            log(formatted)
            
        self.server = socket(sockets.AF_UNIX, sockets.SOCK_STREAM)
        try:
            self.server.connect(self.socket_file)
            self.server.setblocking(True)
            io = sockets.SocketIO(self.server, "rw")
            self.server_IO = io
        except Exception as e:
            error(f"Could not connect to the jumpstart server [{self.socket_file}]")
            log(e)
            self.post_message(self.DirtyExit())
            return
        
        # Jumpstart sends the spec as a dict on connection
        try:
            init = io.readline()
            self.spec = json.loads(init)
        except json.JSONDecodeError as e:
            error("Could not decode handshake", "console")
            log(init.decode())
            log(e)
            self.post_message(self.DirtyExit())
            return
        
        info("Connected")
        
        help_str = "Command Reference:\n"
        
        for command in self.spec["commands"]:
            help_str += f'\t> [bold yellow]{command["name"]}'
            for arg in command["args"]:
                if arg["required"]:
                    arg_str = f' {arg["name"]} {{}}'
                else:
                    arg_str = f' \\[{arg["name"]} {{}}]'
                
                if arg["type"] == "enum":
                    help_str += arg_str.format(f'<{", ".join(arg["values"])}>')
                elif arg["type"] == "list":
                    help_str += arg_str.format("...")
            help_str += "[/bold yellow]\n"
            help_str += f'\t\t [green]{command["desc"]}[/green]\n'

        self.help_str = help_str
        
        while not io.closed:
            line = io.readline()
            
            try:
                msg = json.loads(line)
                if msg["status"] == "E":
                    error(msg["detail"])
                elif msg["status"] == "T":
                    info("Connection closed: " + msg.get("reason") or "Reason unspecified")
                    self.post_message(self.DirtyExit())
                    return
                elif msg["status"] == "I":
                    info(msg["detail"])
                elif msg["status"] == "S":
                    self.post_message(self.Status(
                        msg["frontend"],
                        msg["api"],
                        msg["collection"]
                    ))
            except json.JSONDecodeError:
                error("Bad packet from server", "console")
                log(line)
            except Exception as e:
                error("Exception while reacting to incoming packet", "console")
                log(e)
                log(msg)

def run_app(socket_file = Path("jumpstart.sock"), ctx = None):
    app = JumpstartTUI()
    
    if not socket_file.exists():
        raise ValueError(f"Socket file {str(socket_file.resolve())} does not exist")
    
    app.socket_file = str(socket_file)
    app.run()
    
    if ctx:
        import click
        click.echo("Exited application")
    
    if hasattr(app, "server_IO"):
        # This is duplicated above in case of partial shutdown
        app.server.shutdown(sockets.SHUT_RDWR)
        app.server_IO.close()
        app.server.close()

    # Clean up any residual workers
    app.workers.cancel_all()

if __name__ == "__main__":
    socket_file = Path("jumpstart.sock")
    for arg in argv:
        if arg.startswith("socketfile="):
            socket_file = Path(arg.split("=", 1)[1])
            
    run_app(socket_file)
