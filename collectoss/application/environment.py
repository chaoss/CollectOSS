
def _deprefix(key: str, prefixes: list[str], separator = "_") -> str:
    """Remove a prefix from the provided key


    Args:
        key (str): the key to remove the prefix from
        prefixes (list[str]): the prefixes to look for
        separator (str, optional): the separator between elements of the key to also remove (if they would otherwise be dangling). Defaults to "_".

    Returns:
        str: The key value with the prefix removed if possible, otherwise returns the value of `key`
    """
    unprefixed = None
    for p in prefixes:
        p = p.upper()
        k = key.upper()
        if k.startswith(p):
            unprefixed = key[len(p):]
        
            if unprefixed.startswith(separator):
                unprefixed = unprefixed[len(separator):]
            return unprefixed
    return key


