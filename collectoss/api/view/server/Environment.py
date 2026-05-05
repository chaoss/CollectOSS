import os

class Environment:
    """
    This class is used to make dealing with environment variables easier. It
    allows you to set multiple environment variables at once, and to get items
    with subscript notation without needing to deal with the particularities of
    non-existent values.
    """
    def __init__(self, **kwargs):
        for (key, value) in kwargs.items():
            self[key] = value

    def setdefault(self, key, value):
        if not self[key]:
            self[key] = value
            return value
        return self[key]

    def setall(self, **kwargs):
        result = {}
        for (key, value) in kwargs.items():
            if self[key]:
                result[key] = self[key]
            self[key] = value

    def getany(self, *args):
        result = {}
        for arg in args:
            if self[arg]:
                result[arg] = self[arg]
        return result

    def as_type(self, type, key):
        if self[key]:
            return type(self[key])
        return None

    def __getitem__(self, key):
        return os.getenv(key)

    def __setitem__(self, key, value):
        os.environ[key] = str(value)

    def __len__(self)-> int:
        return len(os.environ)

    def __str__(self)-> str:
        return str(os.environ)

    def __iter__(self):
        return (item for item in os.environ.items())