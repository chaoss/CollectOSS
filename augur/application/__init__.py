def requires_db_session(logger):
    def inner_decorator(fun):
        def wrapper(*args, **kwargs):

            from augur.application.db.session import DatabaseSession

            # create DB session
            with DatabaseSession(logger) as session:

                return fun(session, *args, **kwargs)
        
        return wrapper
    return inner_decorator
