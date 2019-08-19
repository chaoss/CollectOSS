import time
import subprocess
import os
import pytest
import sys

SOURCE = "**"
if len(sys.argv) == 2:
    SOURCE = str(sys.argv[1])

FNULL = open(os.devnull, 'w')

start = subprocess.Popen(['augur', 'run'], stdout=FNULL, stderr=subprocess.STDOUT)
print("Waiting for the server to start...")
time.sleep(20)
process = subprocess.run("pytest -ra augur/datasources/{}/test_{}_routes.py".format(SOURCE, SOURCE), shell=True)
time.sleep(5)
subprocess.Popen(['make', 'backend-stop'])

sys.exit(process.returncode)
