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
    k = key.upper()
    for p in prefixes:
        p_up = p.upper()
        if k == p_up:
            return key[:len(p)]
        if k.startswith(p_up + separator):
            return key[:len(p) + len(separator)]
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
    
    @classmethod
    def get_bool(cls, key:str, default: bool, prefixes = _prefixes) -> bool:
        """gets a value from the environment and cast it to a boolean
        """
        raw_val = cls.get(key, None, prefixes)
        if raw_val is None:
            return default
        return raw_val.lower() in ('true', '1', 't', 'y', 'yes')
        
    @classmethod
    def set(cls, key: str, value: str, overwrite=True) -> None:
        if os.getenv(key) is not None and not overwrite:
            return
        
        os.environ[key] = value

    @classmethod
    def set_default(cls, key: str, value: str) -> None:
        if cls.get(key) is None:
            cls.set(key, value)
            return value
        return cls.get(key)