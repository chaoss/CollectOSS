import os
import pytest
import pandas

@pytest.fixture
def publicwww():
  import ghdata
  return ghdata.GitHub(os.getenv("GITHUB_API_KEY"))