import time
import subprocess
import os
import pytest
import sys

FNULL = open(os.devnull, "w")

start = subprocess.Popen(["augur", "run", "--disable-housekeeper"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Waiting for the server to start...")
time.sleep(15)
process = subprocess.run(["pytest", "-ra", "test/api/"])
time.sleep(2)
subprocess.Popen(["augur", "util", "kill"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Server successfully shutdown.")

sys.exit(process.returncode)
