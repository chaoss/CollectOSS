from sqlalchemy.exc import OperationalError
import time



def catch_operational_error(func):

    attempts = 0
    while attempts < 4:

        # do the sleep here instead of instead of in the exception 
        # so it doesn't sleep after the last failed time
        if attempts > 0:
            time.sleep(240)
        try:
            return func()
        except OperationalError:
            pass

        attempts += 1

    raise Exeption("Unable to Resolve Operational Error")


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





