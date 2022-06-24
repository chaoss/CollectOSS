#SPDX-License-Identifier: MIT
import click
import os
from os import walk

from augur.cli import pass_logs_dir

@click.group("logging", short_help="View Augur's log files")
def cli():
    pass

@cli.command("directory")
@pass_logs_dir
def directory(logs_dir):
    """
    Print the location of Augur's logs directory
    """
    print(logs_dir)

@cli.command("errors")
@click.argument("worker", default="all")
@pass_logs_dir
def errors(logs_dir, worker):
    """
    Output error messages of the main Augur and all worker logfiles or a specific worker logfile
    """
    root_log_dir = logs_dir
    worker_log_dir = logs_dir + "/workers/"
    if worker is None:
        worker = "all"

    if worker == "all":
        files = []
        directories = []
        for (_, _, filenames) in walk(root_log_dir):
            for file in filenames:
                if file.endswith(".err"):
                    print_log(file, root_log_dir)
            break

        files = []
        directories = []
        for (dirpath, dirnames, filenames) in walk(worker_log_dir):
            directories.extend(dirnames)
            break

        for directory in directories:
            specific_worker_log_dir = worker_log_dir + directory
            for (_, _, filenames) in walk(specific_worker_log_dir):
                files.extend(filenames)
                for file in [file for file in filenames if "collection" in file and file.endswith(".err")]:
                    print_log(file, specific_worker_log_dir)
                break
    else:
        files = []
        specific_worker_log_dir = worker_log_dir + "/" + worker + "/"
        for (_, _, filenames) in walk(specific_worker_log_dir):
            files.extend(filenames)
            for file in [file for file in filenames if "collection" in file and file.endswith(".err")]:
                print_log(file, specific_worker_log_dir)
            break

def print_log(file, log_dir):
    f = open(log_dir + "/" + file)
    result = f.readlines()
    print("********** Logfile: " + file)
    for log in result:
        print(log.strip())
    print()

@cli.command("tail")
@click.argument("lines", default=20)
@pass_logs_dir
def tail(logs_dir, lines):
    """
    Output the last n lines of the main Augur and worker logfiles
    """
    root_log_dir = logs_dir
    worker_log_dir = logs_dir + "/workers/"
    if lines is None:
        lines = 20

    files = []
    directories = []
    for (_, _, filenames) in walk(root_log_dir):
        for file in filenames:
            result = _tail(open(root_log_dir + "/" + file), lines)
            print("********** Logfile: " + file)
            for log in result:
                print(log.strip())
            print()
        break

    files = []
    directories = []
    for (dirpath, dirnames, filenames) in walk(worker_log_dir):
        directories.extend(dirnames)
        break

    for directory in directories:
        specific_worker_log_dir = worker_log_dir + directory
        for (_, _, filenames) in walk(specific_worker_log_dir):
            files.extend(filenames)

            for file in [file for file in filenames if "collection" in file]:
                result = _tail(open(specific_worker_log_dir + "/" + file), lines)
                print("********** Logfile: " + file)
                for log in result:
                    print(log.strip())
                print()
            break

def _tail(f, lines=20, _buffer=4098):
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()

        # we found enough lines, get out
        # Removed this line because it was redundant the while will catch
        # it, I left it for history
        # if len(lines_found) > lines:
        #    break

        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1

    return lines_found[-lines:]