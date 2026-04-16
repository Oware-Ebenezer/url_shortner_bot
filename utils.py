"""
utils.py
--------
Pure utility functions with no side effects.
Currently holds URL validation — add other general-purpose helpers here.
"""

from config import URL_REGEX


def is_valid_url(text: str) -> bool:
    return bool(URL_REGEX.match(text.strip()))
