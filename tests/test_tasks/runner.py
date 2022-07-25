import time
import subprocess
import os
import pytest
import sys


start = subprocess.Popen(["celery", "-A", "tasks.celery_init.celery_app worker ", "--loglevel=info", "--concurrency=1"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Waiting for the celery to start...")
time.sleep(5)

process = subprocess.run(["pytest", "tests/test_tasks/"])
time.sleep(2)

subprocess.Popen(["augur", "backend", "kill"], stdout=FNULL, stderr=subprocess.STDOUT)
print("Server successfully shutdown.")
sys.exit(process.returncode)
