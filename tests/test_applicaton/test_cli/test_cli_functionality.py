import os
import pytest
import subprocess


def test_augur():


    FNULL = open(os.devnull, "w")
    process = subprocess.run(["augur", "--help"], stdout=FNULL, stderr=subprocess.STDOUT)

    assert process.returncode == 0
