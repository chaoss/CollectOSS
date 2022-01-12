from tests.test_workers.worker_persistance.util_persistance import *
from tests.test_workers.test_facade.test_facade_contributor_interface.test_endpoints import set_up_repo_groups



def test_insert_facade_contributors_default_basic(database_connection):
    set_up_repo_groups(database_connection)
    
    dummy = DummyFullWorker(database_connection)
    
    dummy.insert_facade_contributors('10')
    dummy.insert_facade_contributors('20')