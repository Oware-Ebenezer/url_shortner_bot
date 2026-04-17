import os
import re

# Load .env file if it exists (local dev only).
# python-dotenv is listed in requirements.txt for this purpose.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed — fine in production

# Bot credentials 
BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")

# External API
TINYURL_API: str = "https://tinyurl.com/api-create.php"
HTTP_TIMEOUT: int = 10  # seconds


URL_REGEX: re.Pattern[str] = re.compile(
    r"^(https?://)"                    # protocol
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*"  # subdomains
    r"[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?"         # domain
    r"\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?"                      # TLD
    r"(?::\d{1,5})?"                                          # optional port
    r"(?:/[^\s]*)?$",                                         # path/query
    re.IGNORECASE,
)
