import time
import subprocess
import pytest
import sys

SOURCE = "**"
if len(sys.argv) == 2:
    SOURCE = str(sys.argv[1])

start = subprocess.Popen(['make', 'backend'])
time.sleep(5)
process = subprocess.run("pytest augur/datasources/{}/test_{}_routes.py".format(SOURCE, SOURCE), shell=True)
time.sleep(2)
subprocess.Popen(['make', 'backend-stop'])

sys.exit(process.returncode)
