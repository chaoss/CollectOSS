"""This module defines the RandomKeyAuth class"""
from typing import List, Optional, Generator

from httpx import Auth, Request, Response
from random import choice
import hashlib


def mask_key(key: str, first: int = 6, last: int = 3, stars: int = 6) -> str:
    """Mask key except for the first and last few characters."""
    if not isinstance(key, str) or len(key) <= (first + last):
        return "*" * stars
    return f"{key[:first]}{'*' * stars}{key[-last:]}"


def key_fingerprint(key: str, length: int = 12) -> str:
    """Return a short non-reversible fingerprint of the key for correlation."""
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return h[:length]


class RandomKeyAuth(Auth):
    """Custom Auth class for httpx that randomly assigns an API key to each request.

    Attributes:
        list_of_keys (List[str]): list of keys to choose from
        header_name (str): name of header to set the key into
        key_format (str): optional format string with {0} placeholder for key
    """

    def __init__(self, list_of_keys: List[str], header_name: str, logger, key_format: Optional[str] = None):
        self.list_of_keys = list_of_keys
        self.header_name = header_name
        self.key_format = key_format
        self.logger = logger

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        """Attach a randomly selected API key to the request headers."""
        if not self.list_of_keys:
            self.logger.error("No valid keys available to make a request.")
            yield request
            return

        key_value = choice(self.list_of_keys)

        # Log only masked or hashed form, never the full key
        masked = mask_key(key_value)
        fingerprint = key_fingerprint(key_value)
        self.logger.debug(f"Key used for request (masked): {masked} | fingerprint: {fingerprint}")

        # Apply formatting if needed
        if self.key_format:
            key_string = self.key_format.format(key_value)
        else:
            key_string = key_value

        # Set header
        request.headers[self.header_name] = key_string
        # sends the request back with modified headers 
        # basically it saves our changes to the request object
        yield request
