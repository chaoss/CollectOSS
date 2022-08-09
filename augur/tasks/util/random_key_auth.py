from httpx import Auth
from random import choice


class RandomKeyAuth(Auth):
    
    # pass a list of keys that are strings
    # pass the name of the header that you would like to be set on the request
    # Optionally pass the key_format. This is a string that contains a {} so the key can be added and applied to the header in the correct way.
    # For example on github the keys are formatted like "token asdfasfdasf" where asdfasfdasf is the key. So for github 
    # the key_format="token {0}"
    def __init__(self, list_of_keys: [str], header_name, key_format=None):
        self.list_of_keys = list_of_keys
        self.header_name = header_name
        self.key_format = key_format

    def auth_flow(self, request):

        # the choice function is from the random library, and gets a random value from a list
        # this gets a random key from the list
        key_value = choice(self.list_of_keys)

        # formats the key string into a format GitHub will accept

        if self.key_format: 
            key_string = self.key_format.format(key_value)
        else:
            key_string = key_value
            
        # set the headers of the request with the new key
        request.headers[self.header_name] = key_string

        # sends the request back with modified headers
        # basically it saves our changes to the request object
        yield request
