import time
import subprocess
import os
import pytest
import sys

FNULL = open(os.devnull, "w")

subprocess.Popen(["augur", "backend", "kill"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Server successfully shutdown.")
