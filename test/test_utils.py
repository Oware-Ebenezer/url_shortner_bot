import pytest
from utils import is_valid_url


class TestValidUrls:
    @pytest.mark.parametrize("url", [
        "https://google.com",
        "http://google.com",
        "https://www.google.com",
        "https://subdomain.example.co.uk",
        "https://example.com/path/to/page",
        "https://example.com/path?query=1&other=2",
        "https://example.com/path#section",
        "https://EXAMPLE.COM",                        # case insensitive
        "https://example.io",
        "https://my-site.org/very/long/path/here",
        "http://localhost.dev",
        "https://example.com/path/with/emoji/✓",      # unicode path
    ])
    def test_accepts_valid_url(self, url):
        assert is_valid_url(url) is True, f"Expected valid but got invalid: {url}"


class TestInvalidUrls:
    @pytest.mark.parametrize("url", [
        "",             
        "   ",             
        "not a url",       
        "ftp://example.com",
        "example.com",        
        "www.example.com",    
        "https://",         
        "https://nodot",  
        "just-text",             
        "http://",                     
        "://example.com",          
        "https://example",                 
    ])
    def test_rejects_invalid_url(self, url):
        assert is_valid_url(url) is False, f"Expected invalid but got valid: {url}"


class TestEdgeCases:
    def test_strips_leading_whitespace(self):
        assert is_valid_url("  https://example.com  ") is True

    def test_http_accepted(self):
        """Plain http:// (not https) must still be valid."""
        assert is_valid_url("http://example.com") is True

    def test_https_required_not_ftp(self):
        assert is_valid_url("ftp://example.com") is False

    def test_long_path_accepted(self):
        url = "https://example.com/" + "a/" * 50
        assert is_valid_url(url) is True

    def test_returns_bool(self):
        result = is_valid_url("https://example.com")
        assert isinstance(result, bool)
