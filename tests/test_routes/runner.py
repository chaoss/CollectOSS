#SPDX-License-Identifier: MIT
import time
import subprocess
import os
import pytest
import sys

from tests import server_port


FNULL = open(os.devnull, "w")

start = subprocess.Popen(["augur", "backend", "start", "--disable-collection", "--port", server_port])
print("Waiting for the server to start...")
time.sleep(10)

if len(sys.argv) > 1:
        process = subprocess.run(["pytest", "tests/test_routes"])
        time.sleep(7)

else:
    process = subprocess.run(["pytest", "tests/test_routes/test_api_functionality"])
    time.sleep(3)

subprocess.Popen(["augur", "backend", "kill"])
print("Server successfully shutdown.")
sys.exit(process.returncode)
