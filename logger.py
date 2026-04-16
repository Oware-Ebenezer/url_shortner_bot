import logging

def setup_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(message)s",
        level=logging.INFO
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name) 