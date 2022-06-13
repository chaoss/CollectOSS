from httpx import Auth
from random import choice


class RandomKeyAuth(Auth):
    def __init__(self, list_of_keys):
        self.list_of_keys = list_of_keys

    def auth_flow(self, request):

        # the choice function is from the random library, and gets a random value from a list
        # this gets a random key from the list
        key = choice(self.list_of_keys)

        # set the headers of the request with the new key
        request.headers['Authorization'] = key

        # sends the request back with modified headers
        # basically it saves our changes to the request object
        yield request
