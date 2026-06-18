def mask_key(key: str, first: int = 6, last: int = 3, stars: int = 6) -> str:
    """Mask key except for the first and last few characters."""
    if key is None:
        return None

    if isinstance(key, str):
        if key == "":
            return "*" * stars + f" Type: empty string"
        if len(key) <= (first + last):
            return "*" * stars
        return f"{key[:first]}{'*' * stars}{key[-last:]}"
    else:
        return "*" * stars + f" Type: {str(type(key))}"
