import os
import importlib
import re
import pytest

class TestBotToken:
    def test_token_is_string(self):
        import config
        assert isinstance(config.BOT_TOKEN,str)
        
    def test_token_reads_from_env(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "test-token-123")
        import config
        importlib.reload(config)
        assert config.BOT_TOKEN == "test-token-123"
        
    def test_token_empty_when_env_missing(self, monkeypatch):
        monkeypatch.delenv("BOT_TOKEN", raising = False)
        import config
        importlib.reload(config)
        assert config.BOT_TOKEN == ""
        
class TestConstants:
    def test_tinyurl_api_is_https(self):
        import config
        assert config.TINYURL_API.startswith("https://")
        
    def test_http_timeout_is_positive_int(self):
        import config
        assert isinstance(config.HTTP_TIMEOUT, int)
        assert config.HTTP_TIMEOUT > 0

    def test_url_regex_is_compiled(self):
        import config
        assert isinstance(config.URL_REGEX, re.Pattern)