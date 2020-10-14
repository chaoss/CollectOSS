#SPDX-License-Identifier: MIT
import time
import subprocess
import os
import pytest
import sys

FNULL = open(os.devnull, "w")

start = subprocess.Popen(["augur", "backend", "start", "--disable-housekeeper", "--skip-cleanup"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Waiting for the server to start...")
time.sleep(5)

process = subprocess.run(["pytest", "tests/test_routes/"])
time.sleep(2)

subprocess.Popen(["augur", "backend", "kill"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Server successfully shutdown.")
sys.exit(process.returncode)
