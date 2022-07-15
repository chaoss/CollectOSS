from httpx import Auth
from random import choice


class RandomKeyAuth(Auth):
    def __init__(self, list_of_keys: [str]):
        self.list_of_keys = list_of_keys

    def auth_flow(self, request):

        # the choice function is from the random library, and gets a random value from a list
        # this gets a random key from the list
        key_value = choice(self.list_of_keys)

        # formats the key string into a format GitHub will accept
        key_string = f"token {key_value}"

        # set the headers of the request with the new key
        request.headers['Authorization'] = key_string

        # sends the request back with modified headers
        # basically it saves our changes to the request object
        yield request
