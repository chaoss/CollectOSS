import click
import os
from os import walk
from augur.logging import AUGUR_LOG_DIR, WORKER_LOG_DIR

@click.group("logging", short_help="View Augur's log files")
def cli():
    pass

@cli.command("directory")
def directory():
    """
    Print the location of Augur's logs directory
    """
    print(AUGUR_LOG_DIR)

@cli.command("tail")
@click.argument("lines", default=20)
def tail(lines):
    """
    Output the last n lines of the main Augur and worker logfiles
    """
    if lines is None:
        lines = 20

    files = []
    directories = []
    for (_, _, filenames) in walk(AUGUR_LOG_DIR):
        for file in filenames:
            result = tail(open(AUGUR_LOG_DIR + "/" + file), lines)
            print("********** Logfile: " + file)
            for log in result:
                print(log.strip())
            print()
        break

    files = []
    directories = []
    for (dirpath, dirnames, filenames) in walk(WORKER_LOG_DIR):
        directories.extend(dirnames)
        break

    for directory in directories:
        specific_worker_log_dir = WORKER_LOG_DIR + directory
        for (_, _, filenames) in walk(specific_worker_log_dir):
            files.extend(filenames)

            for file in [file for file in filenames if "collection" in file]:
                result = tail(open(specific_worker_log_dir + "/" + file), lines)
                print("********** Logfile: " + file)
                for log in result:
                    print(log.strip())
                print()
            break

def tail(f, lines=20, _buffer=4098):
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