import socket as sockets
from socket import socket

import json
import logging
from sys import argv
from pathlib import Path
from datetime import datetime

from textual import work
from textual.app import App, on
from textual.binding import Binding
from textual.events import Load, Mount
from textual.widgets import RichLog, Input, Button
from textual.containers import Horizontal, Vertical

class JumpstartTUI(App):
    CSS_PATH = "tui.tcss"
    
    BINDINGS = [
        Binding("ctrl+d", "kb_exit", "Exit", priority=True)
    ]
    
    def action_kb_exit(self, force = False):
        inbox = self.query(Input).only_one()
        value = inbox.value
        
        if not value or force:
            self.app.exit()
    
    def exit_dirty(self):
        inbox = self.query(Input).only_one()
        inbox.value = ""
        inbox.disabled = True
        
        self.error("Use CTRL+D or CTRL+C to exit")
        
    def error(self, msg):
        self.out("ERROR", msg)
    
    def info(self, msg):
        self.out("INFO", msg)
        
    def out(self, level, msg, source = "console"):
        time_str = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        formatted = "[{}] [{}] [{}] {}".format(time_str, source, level, msg)
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
    
    @on(Mount)
    async def startup_process_tasks(self):
        inbox = self.query(Input).only_one()
        inbox.focus()
        
        self.server_rec()
    
    @on(Button.Pressed, "#exitbtn")
    def handle_btn_exit(self):
        self.action_kb_exit(True)
    
    @on(Input.Submitted)
    def accept_input(self):
        inbox = self.query(Input).only_one()
        value = inbox.value
        
        if value == "exit":
            self.action_kb_exit(True)
        
        self.out("INFO", value, "user")
        inbox.value = ""
        
        args = value.split()
        
        if args[0] == "help":
            self.show_help(*args[1:])
    
    def send(self, **kwargs):
        self.server_IO.write((json.dumps(kwargs) + "\n").encode())
        self.server_IO.flush()
    
    @on(Button.Pressed, "#statusbtn")
    def get_status(self):
        self.send({
            "name": "status"
        })
        self.info("Status requested")
    
    def show_help(self, command = None, *args):
        if not command:
            self.raw(self.help_str, True, True)
        else:
            self.info("Granular help not yet available")
    
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
            self.call_from_thread(self.exit_dirty)
            return
        
        # Jumpstart sends the spec as a dict on connection
        try:
            import time
            init = io.readline()
            self.spec = json.loads(init)
        except json.JSONDecodeError as e:
            error("Could not decode handshake", "console")
            log(e)
            self.call_from_thread(self.exit_dirty)
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
                if msg["ID"] == "E":
                    error(msg["detail"])
                elif msg["ID"] == "T":
                    info("Connection closed: " + msg.get("reason") or "Reason unspecified")
                    self.call_from_thread(self.exit_dirty)
                    return
                elif msg["ID"] == "I":
                    info(msg["detail"])
                elif msg["ID"] == "S":
                    ...
            except json.JSONDecodeError:
                error("Bad packet from server", "console")
                log(line)
            except Exception:
                error("Exception while reacting to incoming packet", "console")
                log(msg)
        
    def compose(self):
        with Horizontal():
            with Vertical(classes="sidebar"):
                yield Button("Status")
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

def run_app(socket_file = Path("jumpstart.sock"), ctx = None):
    app = JumpstartTUI()
    
    if not socket_file.exists():
        raise ValueError(f"Socket file {str(socket_file.resolve())} does not exist")
    
    app.socket_file = str(socket_file)
    app.run()
    
    if ctx:
        import click
        click.echo("Exited application")
    
    if app.server_IO:
        app.server.shutdown(sockets.SHUT_RDWR)
        app.server_IO.close()
        app.server.close()

    # Clean up any residual threads
    app.workers.cancel_all()

if __name__ == "__main__":
    socket_file = Path("jumpstart.sock")
    for arg in argv:
        if arg.startswith("socketfile="):
            socket_file = Path(arg.split("=", 1)[1])
            
    run_app(socket_file)
