import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

#Mocking Telegram Objects
def _make_message(text: str = "") -> MagicMock:
    message = MagicMock()
    message.text = text
    message.reply_text = AsyncMock()
    message.edit_text = AsyncMock()
    return message

def _make_update(text: str = "") -> MagicMock:
    update = MagicMock()
    update.message = _make_message(text)
    return update

def _make_context(args: list[str] | None = None) -> MagicMock:
    context = MagicMock()
    context.args = args or []
    return context


@pytest.fixture
def mock_update():
    return _make_update()


@pytest.fixture
def mock_context():
    return _make_context()

@pytest.fixture
def make_update():
   
    return _make_update

@pytest.fixture
def make_context():
    return _make_context()