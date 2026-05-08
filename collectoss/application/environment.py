from typing import Optional
import os
import warnings
import logging

logger = logging.getLogger(__name__)

def extract_prefix(key: str, prefixes: list[str], separator = "_") -> Optional[str]:
    """Detect and return the prefix present on the provided key

    Args:
        key (str): the key to remove the prefix from
        prefixes (list[str]): the prefixes to look for
        separator (str, optional): the separator between elements of the key to also remove (if they would otherwise be dangling). Defaults to "_".

    Returns:
        str: The detected prefix (including any separators) if any, otherwise None
    """
    prefix_len = 0
    for p in prefixes:
        p = p.upper()
        k = key.upper()
        if k.startswith(p):
            prefix_len += len(p)

            if k[prefix_len] == separator:
                prefix_len += len(separator)
            return key[0:prefix_len]
    return None


class SystemEnv:
    """Centralized environment variable access
    Built for enabling migration of environment variable names
    """

    _prefixes = ["COLLECTOSS", "AUGUR"]
    _warn_prefixes = ["AUGUR"]
    _separator = "_"

    @classmethod
    def get(cls, key: str, default = None, prefixes = _prefixes) -> Optional[str]:
        # extract the suffix so we can try multiple prefixes
        canonical_prefix = extract_prefix(key, prefixes, cls._separator)
        suffix = key[len(canonical_prefix):] if canonical_prefix is not None else key
        # check prefixes in order and use the first one that has a value
        for p in prefixes:
            check_key = f"{p}{cls._separator}{suffix}"
            value = os.getenv(check_key, None)

            if value is not None:
                # emit a warning if configured
                if p in cls._warn_prefixes:
                    msg = (
                        f"Environment variable '{check_key}' is deprecated. "
                        f"Use '{key}' instead. This automatic recovery may become a failure in a future version "
                    )
                    logger.warning(msg)
                    warnings.warn(msg, DeprecationWarning, stacklevel=2)
                
                return value

        if not canonical_prefix:
            return os.getenv(key, default)
        
        return default
