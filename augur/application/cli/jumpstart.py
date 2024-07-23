import psutil
import click
import time
import subprocess
from pathlib import Path
from datetime import datetime

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        p = check_running()
        if not p:
            click.echo("Jumpstart is not running. Start it with: augur jumpstart run")
            return

        click.echo(f"Connecting to Jumpstart: [{p.pid}]")
        
        while p.is_running() and not len(p.connections("unix")):
            # Waiting for app to open fd socket
            time.sleep(0.1)
        
        if not p.is_running():
            click.echo("Error: Jumpstart server exited abnormally")
        
        from jumpstart.tui import run_app
        run_app(ctx=ctx)
        
def check_running(pidfile = ".jumpstart.pid") -> psutil.Process:
    jumpidf = Path(pidfile)
    
    try:
        jumpid, create_time = jumpidf.read_text().splitlines()
        jumpp = psutil.Process(int(jumpid))
        
        if create_time != str(jumpp.create_time()):
            # PID was reused, not the original
            jumpidf.unlink()
            return
        
        return jumpp
    except (psutil.NoSuchProcess, FileNotFoundError):
        return
    except PermissionError:
        click.echo(f"Permission denied while reading from or writing to pidfile [{str(jumpidf.resolve())}]")

@cli.command("status")
def get_status():
    p = check_running()
    
    if not p:
        click.echo("Jumpstart is not running")
    else:
        since = datetime.fromtimestamp(p.create_time()).astimezone()
        delta = datetime.now().astimezone() - since
        click.echo(f"Jumpstart is running at: [{p.pid}] since {since.strftime('%a %b %d, %Y %H:%M:%S %z:%Z')} [{delta}]")

@cli.command("run")
@click.pass_context
def startup(ctx):
    p = check_running()

    if not p:
        click.echo("Starting")
        p = launch(ctx)
    else:
        click.echo(f"Jumpstart is already running [{p.pid}]")

@cli.command("processID")
def get_main_ID():
    p = check_running()
    
    if p:
        click.echo(p.pid)

@cli.command("shutdown")
def shutdown_server():
    p = check_running()
    
    if not p:
        click.echo("Jumpstart is not running")
        return
    
    click.echo("Blocking on shutdown")
    p.terminate()
    p.wait()

def launch(ctx, pidfile = ".jumpstart.pid", socketfile = "jumpstart.sock"):
    service = subprocess.Popen(f"python -m jumpstart.jumpstart pidfile={pidfile} socketfile={socketfile}".split())
    
    # Popen object does not have create_time for some reason
    ext_process = psutil.Process(service.pid)

    with open(pidfile, "w") as file:
        file.write(f"{ext_process.pid}\n{ext_process.create_time()}")
    
    return ext_process
