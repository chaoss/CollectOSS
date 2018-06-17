import os
import pytest
import pandas

@pytest.fixture
def librariesio():
    import augur
    augurApp = augur.Application()
    return augurApp.librariesio()

# *** DIVERSITY AND INCLUSION *** #

# *** GROWTH, MATURITY, AND DECLINE *** #

# *** RISK *** #

# *** VALUE *** #

# *** ACTIVITY *** #

# *** EXPERIMENTAL *** #

# These tests are broken
# def test_dependencies(librariesio):
#     assert librariesio.dependencies('rails', 'rails').isin('[blade]').any

# def test_dependents(librariesio):
#     assert librariesio.dependents('rails', 'rails').isin('[haml]').any
