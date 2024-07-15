import psutil
import click
import subprocess
from pathlib import Path
from datetime import datetime

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        p = check_running()
        if not p:
            click.echo("Starting service")
            launch(ctx)
        else:
            click.echo(f"Connecting to Jumpstart: [{p.pid}]")

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

@cli.command("processID")
def get_main_ID():
    p = check_running()
    
    if p:
        click.echo(p.pid)

def launch(ctx, pidfile = ".jumpstart.pid"):
    service = subprocess.Popen(f"python scripts/control/jumpstart.py pidfile={pidfile}".split())
    
    # Popen object does not have create_time for some reason
    ext_process = psutil.Process(service.pid)

    with open(pidfile, "w") as file:
        file.write(f"{ext_process.pid}\n{ext_process.create_time()}")
