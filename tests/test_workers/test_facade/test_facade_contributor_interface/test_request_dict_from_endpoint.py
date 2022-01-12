from tests.test_workers.worker_persistance.util_persistance import *

def test_request_dict_from_endpoint_good_values(database_connection):
    dummy = DummyFullWorker(database_connection)
    
    good_values = [
        'https://api.github.com/users/IsaacMilarky',
        'https://api.github.com/users/dlumbrer',
        'https://api.github.com/repos/chaoss/augur/contributors',
        'https://api.github.com/repos/chaoss/augur/commits/53b0cc122ac9ecc1588d76759dc2e8e437f45b48'
    ]
    
    for value in good_values:
        data = dummy.request_dict_from_endpoint(value)
        
        if data == None:
            raise AssertionError


def test_request_dict_from_endpoint_bad_values(database_connection):
    dummy = DummyFullWorker(database_connection)
    
    bad_values = [
        'https://api.github.com/',
        'https://github.com/users/IsaacMilarky',
        ' ',
        '\n ',
        'RandomString',
        'https://google.com'
    ]
    
    for value in bad_values:
        data = dummy.request_dict_from_endpoint(value)
        
        if data != None:
            raise AssertionError
        