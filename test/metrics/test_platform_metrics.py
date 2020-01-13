#SPDX-License-Identifier: MIT

import pytest

@pytest.fixture(scope="module")
def metrics():
    import augur
    augur_app = augur.Application()
    return augur_app.metrics
