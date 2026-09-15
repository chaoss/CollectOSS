# SPDX-License-Identifier: MIT
from importlib.metadata import version, PackageNotFoundError

_FALLBACK_VERSION = "unknown"
_PACKAGE_NAME = "collectoss"


def get_version() -> str:
    """Return the installed version of CollectOSS.

    Falls back to 'unknown' if the package metadata is not available
    (e.g. running from source without installing).
    """
    try:
        return version(_PACKAGE_NAME)
    except PackageNotFoundError:
        return _FALLBACK_VERSION


def get_user_agent() -> str:
    """Return the User-Agent string CollectOSS should send with API requests.

    Format: CollectOSS/<version> (github:chaoss/collectoss; CHAOSS/Linux Foundation)
    """
    return f"CollectOSS/{get_version()} (github:chaoss/collectoss; CHAOSS/Linux Foundation)"
