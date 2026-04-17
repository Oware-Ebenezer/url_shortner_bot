from config import URL_REGEX


def is_valid_url(text: str) -> bool:
    return bool(URL_REGEX.match(text.strip()))
