#SPDX-License-Identifier: MIT
import time
import subprocess
import os
import pytest
import sys

FNULL = open(os.devnull, "w")

start = subprocess.Popen(["augur", "backend", "start", "--disable-collection"])
print("Waiting for the server to start...")
time.sleep(10)

process = subprocess.run(["pytest", "tests/test_routes/"])
time.sleep(5)

subprocess.Popen(["augur", "backend", "kill"])
print("Server successfully shutdown.")
sys.exit(process.returncode)
