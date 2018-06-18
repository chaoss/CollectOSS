import os
import pytest
import pandas

@pytest.fixture
def ghtorrentplus():
    import augur
    augurApp = augur.Application()
    return augurApp.ghtorrentplus()

# *** DIVERSITY AND INCLUSION *** #

# *** GROWTH, MATURITY, AND DECLINE *** #
def test_closed_issue_resolution_duration(ghtorrentplus):
    assert ghtorrentplus.closed_issue_resolution_duration('mopidy', 'mopidy').isin(["2012-11-10T09:51:19.000Z"]).any

# *** RISK *** #

# *** VALUE *** #

# *** ACTIVITY *** #

# *** EXPERIMENTAL *** #
