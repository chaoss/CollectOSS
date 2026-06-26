import logging
import pytest
import sqlalchemy as s

from collectoss.tasks.util.worker_util import remove_duplicates_by_uniques, batched

logger = logging.getLogger(__name__)

@pytest.mark.unit
def test_remove_duplicates_by_uniques():

    data_1 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "bob", "cntrb_id": "01003f7a-8500-0000-0000-000000000000"}
    data_2 = {"cntrb_login": "amazing", "gh_user_id": 1700, "gh_login": "hello", "cntrb_id": "01003f7a-8500-0000-0000-000123002000"}
    data_3 = {"cntrb_login": "cool_guy", "gh_user_id": 230, "gh_login": "lame_guy", "cntrb_id": "01003f7a-8511-0000-0000-000123875000"}
    data_4 = {"cntrb_login": "great", "gh_user_id": 230, "gh_login": "boring", "cntrb_id": "01003f7a-8511-0000-0000-000123000000"}
    all_data = [data_4, data_1, data_3, data_1, data_2, data_1, data_3, data_4, data_2]

    assert len(remove_duplicates_by_uniques(all_data, ["cntrb_id"])) == 4

    data_1 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "bob", "cntrb_id": "01003f7a-8500-0000-0000-000123002000"}
    data_2 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "hello", "cntrb_id": "01003f7a-8500-0000-0000-000123002000"}

    assert len(remove_duplicates_by_uniques([data_1, data_2], ["cntrb_id", "gh_user_id"])) == 1

    data_1 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "bob", "cntrb_id": "01003f7a-8500-0000-0000-000000000000"}
    data_2 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "hello", "cntrb_id": "01003f7a-8500-0000-0000-000123002000"}
    data_3 = {"cntrb_login": "Bob", "gh_user_id": 4, "gh_login": "hello", "cntrb_id": "01003f7a-8500-0000-0000-000123042000"}

    assert len(remove_duplicates_by_uniques([data_1, data_2], ["cntrb_id", "gh_user_id", "gh_login"])) == 2


class TestBatched:
    @pytest.mark.unit
    def test_batched_evenly_divisible(self):
        result = list(batched([1, 2, 3, 4, 5, 6], 3))
        assert result == [[1, 2, 3], [4, 5, 6]]


    @pytest.mark.unit
    def test_batched_remainder(self):
        result = list(batched([1, 2, 3, 4, 5], 3))
        assert result == [[1, 2, 3], [4, 5]]


    @pytest.mark.unit
    def test_batched_smaller_than_batch_size(self):
        result = list(batched([1, 2], 100))
        assert result == [[1, 2]]


    @pytest.mark.unit
    def test_batched_empty(self):
        result = list(batched([], 3))
        assert result == []


    @pytest.mark.unit
    def test_batched_size_one(self):
        result = list(batched([1, 2, 3], 1))
        assert result == [[1], [2], [3]]


    @pytest.mark.unit
    def test_batched_consumes_generator_lazily(self):
        consumed = []

        def tracking_gen():
            for i in range(6):
                consumed.append(i)
                yield i

        gen = batched(tracking_gen(), 3)

        next(gen)
        assert consumed == [0, 1, 2], "should only have consumed first batch"

        next(gen)
        assert consumed == [0, 1, 2, 3, 4, 5]


    @pytest.mark.unit
    def test_batched_returns_lists(self):
        result = list(batched(range(4), 2))
        assert all(isinstance(chunk, list) for chunk in result)
    