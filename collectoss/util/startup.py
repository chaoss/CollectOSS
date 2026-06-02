## Startup helpers


def check_init_schema():
    """Initialize the CollectOSS database schema as appropriate
    """

    pass
    # does public.alembic_version exist?
        # if yes, do nothing
        # if no, do a sanity check to make sure the other schemas dont exist,
        #   then init the current db with sqlalchemy and stamp the current version with alembic

def check_update_schema():
    """ensure the CollectOSS schema is on the latest version
    """
    pass
    # alembic upgrade head, unless theres an env var preventing automatic migration
    # check_call(["alembic", "upgrade", "head"])

