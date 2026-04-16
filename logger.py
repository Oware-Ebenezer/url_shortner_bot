import logging

def setup_logging() -> None:
    logging.basicConfig(
        format="%(asctimes)s | %(levelname)s | %(messages)s",
        level=logging.INFO
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name) 