import time
import subprocess
import os
import pytest
import sys

SOURCE = "**"
if len(sys.argv) == 2:
    SOURCE = str(sys.argv[1])

test_location_string = "augur/metrics/{source}/test_{source}_routes.py".format(source=SOURCE)

FNULL = open(os.devnull, "w")

start = subprocess.Popen(["augur", "run", "--disable-housekeeper"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Waiting for the server to start...")
time.sleep(15)
process = subprocess.run(["pytest", "-ra", test_location_string])
time.sleep(2)
subprocess.Popen(["augur", "util", "kill"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Server successfully shutdown.")

sys.exit(process.returncode)
