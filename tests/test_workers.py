import pytest

import workers.repo_info_worker.repo_info_worker.runtime as ri

def test_workers():
    # print(dir(runtime))
    ri.run()
    assert 0