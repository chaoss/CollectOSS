import requests
import pytest

from metric_status_worker.worker import MetricsStatus

def test_get_metric_index_in_table_row():
    row = "metric |sTatuS|TestString"
    metric_status = MetricsStatus("api.github.com")
    result = metric_status.get_metric_index_in_table_row(row)
    print(result)
    assert result == (0, 3)

def test_is_has_link():
    metric_status = MetricsStatus("api.github.com")
    re_result = metric_status.is_has_link("   [oss](augur"  , None)
    assert re_result == ('oss', 'augur')
