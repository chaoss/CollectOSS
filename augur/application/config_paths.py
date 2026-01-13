# SPDX-License-Identifier: MIT
"""Centralized config path utilities."""
import os
from pathlib import Path


def get_config_dir() -> Path:
    """Get config directory from CONFIG_DATADIR env var, or current directory."""
    return Path(os.getenv("CONFIG_DATADIR", "."))


def get_db_config_path() -> Path:
    """Get path to db.config.json."""
    return get_config_dir() / "db.config.json"


def get_augur_config_path() -> Path:
    """Get path to augur.json."""
    return get_config_dir() / "augur.json"


def get_view_config_path() -> Path:
    """Get path to config.yml. Uses CONFIG_LOCATION if set."""
    config_location = os.getenv("CONFIG_LOCATION")
    if config_location:
        return Path(config_location)
    return get_config_dir() / "config.yml"

