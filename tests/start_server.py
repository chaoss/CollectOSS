import time
import subprocess
import os
import sys

from tests import server_port


FNULL = open(os.devnull, "w")

start = subprocess.Popen(["augur", "backend", "start", "--disable-collection", "--port", server_port], stdout=FNULL, stderr=subprocess.STDOUT)
print("Waiting for the server to start...")
time.sleep(10)