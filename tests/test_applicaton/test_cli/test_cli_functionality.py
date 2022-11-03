import os
import pytest


def test_augur():

    exit_status = os.system('augur --help')
    assert exit_status == 0