# SPDX-License-Identifier: MIT
import re

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+$")


def normalize_email(email: str) -> str:
    """Return the email stripped and lowercased, or raise ValueError.

    The check is deliberately loose: it only requires one "@" with text on
    both sides and no whitespace. Real commit emails come in many forms
    (noreply addresses, odd domains), so a strict check would reject valid data.
    """
    email = (email or "").strip().lower()
    if not _EMAIL.match(email):
        raise ValueError("expected an email address such as name@example.com")
    return email