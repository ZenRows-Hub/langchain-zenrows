"""Integration tests for ZenRows Universal Scraper.

These tests make real API calls to ZenRows and require a valid API key.
Set ZENROWS_API_KEY environment variable to run these tests.
"""

import json
import os
import pytest
from langchain_zenrows import ZenRowsUniversalScraper


# Skip all integration tests if no API key is available
pytestmark = pytest.mark.skipif(
    not os.environ.get("ZENROWS_API_KEY"),
    reason="ZENROWS_API_KEY environment variable not set",
)


@pytest.mark.integration
class TestZenRowsUniversalScraperIntegration:
    """Integration tests that make real API calls."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        return ZenRowsUniversalScraper()

    @pytest.fixture
    def test_url(self):
        """Test URL that should work reliably."""
        return "https://httpbin.io/html"

    @pytest.fixture
    def test_url_json(self):
        """Test URL that returns JSON."""
        return "https://httpbin.io/json"

    def test_basic_scraping(self, scraper, test_url):
        """Test basic HTML scraping without any special features."""
        result = scraper.invoke({"url": test_url})

        assert isinstance(result, str)
        assert len(result) > 0
        assert "<html" in result.lower()
        assert "</html>" in result.lower()

    def test_javascript_rendering(self, scraper):
        """Test JavaScript rendering on a page that requires it."""
        js_test_url = "https://www.scrapingcourse.com/javascript-rendering"

        result = scraper.invoke({"url": js_test_url, "js_render": True, "wait": 2000})

        assert isinstance(result, str)
        assert len(result) > 0
        assert "chaz kangeroo hoodie" in result.lower()
        # Should contain content that's loaded by JavaScript

    def test_markdown_response_type(self, scraper, test_url):
        """Test converting response to markdown format."""
        result = scraper.invoke({"url": test_url, "response_type": "markdown"})

        assert isinstance(result, str)
        assert len(result) > 0
        # Markdown should be different from HTML
        assert "<html" not in result.lower()

    def test_css_extraction(self, scraper, test_url):
        """Test CSS selector-based extraction."""
        css_selector = json.dumps({"title": "h1", "content": "p"})

        result = scraper.invoke({"url": test_url, "css_extractor": css_selector})

        assert isinstance(result, str)
        assert len(result) > 0
        assert "herman melville" in result.lower()

    def test_wait_for_selector(self, scraper, test_url):
        """Test waiting for a specific CSS selector."""
        wait_test_url = "https://www.scrapingcourse.com/ecommerce/"
        result = scraper.invoke(
            {"url": wait_test_url, "wait_for": ".product-name", "wait": 1000}
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert "abominable hoodie" in result.lower()

    def test_error_handling_invalid_url(self, scraper):
        """Test error handling with invalid URL."""
        with pytest.raises(ValueError) as exc_info:
            scraper.invoke({"url": "not-a-valid-url"})

        # Should get a meaningful error message
        error_msg = str(exc_info.value).lower()
        assert any(
            keyword in error_msg for keyword in ["url", "invalid", "failed", "error"]
        )

    def test_error_handling_non_existent_domain(self, scraper):
        """Test error handling with non-existent domain."""
        with pytest.raises(ValueError) as exc_info:
            scraper.invoke(
                {"url": "https://this-domain-definitely-does-not-exist-12345.com"}
            )

        # Should get a meaningful error message
        error_msg = str(exc_info.value).lower()
        assert any(
            keyword in error_msg for keyword in ["failed", "error", "connection"]
        )

    def test_multiple_parameters_combination(self, scraper):
        """Test combining multiple parameters."""
        result = scraper.invoke(
            {
                "url": "https://httpbin.io/html",
                "js_render": True,
                "wait": 1000,
                "response_type": "markdown",
            }
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_session_management(self, scraper):
        """Test session management functionality."""
        session_id = 12345

        # Make first request with session
        result1 = scraper.invoke(
            {"url": "https://httpbin.io/ip", "session_id": session_id}
        )

        # Make second request with same session
        result2 = scraper.invoke(
            {"url": "https://httpbin.io/ip", "session_id": session_id}
        )

        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert len(result1) > 0
        assert len(result2) > 0

    def test_block_resources(self, scraper, test_url):
        """Test blocking resources to speed up scraping."""
        result = scraper.invoke(
            {"url": test_url, "block_resources": "image,font", "js_render": True}
        )

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.slow
    def test_large_page_handling(self, scraper):
        """Test handling of large pages."""
        # This test is marked as slow since it might take longer
        large_page_url = (
            "https://www.g2.com/products/asana/reviews"  # Use a known working URL
        )

        result = scraper.invoke(
            {
                "url": large_page_url,
                "js_render": True,
                "premium_proxy": True,
                "wait": 5000,
            }
        )

        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.integration
@pytest.mark.slow
class TestZenRowsLongRunningIntegration:
    """Long-running integration tests."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        return ZenRowsUniversalScraper()

    def test_complex_javascript_page(self, scraper):
        """Test scraping a complex JavaScript-heavy page."""
        # Use a page that requires significant JS processing
        complex_url = "https://www.scrapingcourse.com/javascript-rendering"

        result = scraper.invoke({"url": complex_url, "js_render": True, "wait": 5000})

        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.integration
class TestZenRowsErrorScenarios:
    """Test various error scenarios with real API."""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        return ZenRowsUniversalScraper()

    def test_invalid_api_key_error(self):
        """Test behavior with invalid API key."""
        invalid_scraper = ZenRowsUniversalScraper(zenrows_api_key="invalid-key-12345")

        with pytest.raises(ValueError) as exc_info:
            invalid_scraper.invoke({"url": "https://httpbin.io/html"})

        assert "Invalid ZenRows API key" in str(exc_info.value)

    def test_malformed_css_extractor_real_api(self, scraper):
        """Test malformed CSS extractor with real API call."""
        # This should fail at the Pydantic validation level
        with pytest.raises(Exception):  # Could be ValidationError or ValueError
            scraper.invoke(
                {
                    "url": "https://httpbin.io/html",
                    "css_extractor": "invalid json string",
                }
            )

    def test_invalid_country_code_real_api(self, scraper):
        """Test invalid country code with real API."""
        # This should fail at the Pydantic validation level
        with pytest.raises(Exception):  # Could be ValidationError or ValueError
            scraper.invoke(
                {
                    "url": "https://httpbin.io/html",
                    "proxy_country": "invalid-country-code",
                }
            )
