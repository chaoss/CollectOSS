from typing import Optional

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

