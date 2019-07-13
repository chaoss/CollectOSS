import time
import subprocess
import pytest
import sys

SOURCE = "**"
if len(sys.argv) == 2:
    SOURCE = str(sys.argv[1])

subprocess.Popen(['make', 'backend-restart'])
time.sleep(5)
process = subprocess.run([f'pytest augur/datasources/{SOURCE}/test_{SOURCE}_routes.py'], shell=True)
time.sleep(2)
subprocess.Popen(['make', 'backend-stop'])

sys.exit(process.returncode)
