# -*- coding: utf-8 -*-

"""Version information for ComPath-Utils."""

__all__ = [
    'VERSION',
    'get_version',
]

VERSION = '0.3.2-dev'


def get_version() -> str:
    """Get the current software version of compath-utils."""
    return VERSION
