from sqlalchemy.exc import OperationalError
import time



def catch_operational_error(func):

    attempts = 0
    error = None
    timeout = 240

    while attempts < 4:

        # do the sleep here instead of instead of in the exception 
        # so it doesn't sleep after the last failed time
        if attempts > 0:
            #Do a 30% exponential backoff
            time.sleep(timeout)
            timeout = int(timeout * 1.3)
        try:
            return func()
        except OperationalError as e:
            print(f"ERROR: {e}")
            error = str(e)

        attempts += 1

    raise Exception(error)


def execute_session_query(query, query_type="all"):

    func = None
    if query_type == "all":
        func = query.all
    elif query_type == "one":
        func = query.one
    elif query_type == "first":
        func = query.first
    else:
        raise Exception(f"ERROR: Unsupported query type '{query_type}'")

    return catch_operational_error(func)



def convert_orm_list_to_dict_list(result):
    new_list = []

    for row in result:
        row_dict = row.__dict__
        try:
            del row_dict['_sa_instance_state']
        except:
            pass
        
        new_list.append(row_dict)
    
    return new_list

