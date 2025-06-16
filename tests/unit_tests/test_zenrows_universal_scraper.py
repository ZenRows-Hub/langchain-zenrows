"""Unit tests for ZenRows Universal Scraper."""

import json
import os
import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError

from langchain_zenrows import (
    ZenRowsUniversalScraper,
    ZenRowsUniversalScraperInput,
    ZenRowsUniversalScraperAPIWrapper,
)


class TestZenRowsUniversalScraperInput:
    """Test the Pydantic input schema."""

    def test_minimal_valid_input(self):
        """Test input with only required field."""
        input_data = ZenRowsUniversalScraperInput(url="https://httpbin.io/html")
        assert input_data.url == "https://httpbin.io/html"
        assert input_data.js_render is False
        assert input_data.premium_proxy is False

    def test_full_input_with_all_parameters(self):
        """Test input with all parameters."""
        css_extractor = json.dumps({"title": "h1", "content": "p"})

        input_data = ZenRowsUniversalScraperInput(
            url="https://httpbin.io/html",
            js_render=True,
            js_instructions="""[{"scroll_y": 1500}]""",
            premium_proxy=True,
            proxy_country="us",
            session_id=12345,
            wait_for=".content",
            wait=2000,
            block_resources="images,fonts",
            response_type="markdown",
            css_extractor=css_extractor,
        )

        assert input_data.url == "https://httpbin.io/html"
        assert input_data.js_render is True
        assert input_data.premium_proxy is True
        assert input_data.proxy_country == "us"
        assert input_data.session_id == 12345
        assert input_data.wait_for == ".content"
        assert input_data.wait == 2000
        assert input_data.response_type == "markdown"
        assert input_data.css_extractor == css_extractor

    def test_invalid_css_extractor(self):
        """Test invalid JSON in css_extractor."""
        with pytest.raises(ValidationError) as exc_info:
            ZenRowsUniversalScraperInput(
                url="https://example.com", css_extractor="invalid json"
            )
        assert "css_extractor must be valid JSON" in str(exc_info.value)

    def test_invalid_proxy_country(self):
        """Test invalid proxy_country format."""
        with pytest.raises(ValidationError) as exc_info:
            ZenRowsUniversalScraperInput(
                url="https://example.com", proxy_country="usa"  # Should be 2 letters
            )
        assert "proxy_country must be a two-letter country code" in str(exc_info.value)

    def test_valid_proxy_country(self):
        """Test valid proxy_country format."""
        input_data = ZenRowsUniversalScraperInput(
            url="https://example.com", proxy_country="us"
        )
        assert input_data.proxy_country == "us"

    def test_valid_css_extractor(self):
        """Test valid JSON in css_extractor."""
        css_extractor = json.dumps({"title": "h1"})
        input_data = ZenRowsUniversalScraperInput(
            url="https://example.com", css_extractor=css_extractor
        )
        assert input_data.css_extractor == css_extractor

    def test_response_type_options(self):
        """Test valid response_type options."""
        for response_type in ["markdown", "plaintext", "pdf"]:
            input_data = ZenRowsUniversalScraperInput(
                url="https://example.com", response_type=response_type
            )
            assert input_data.response_type == response_type

    def test_missing_url(self):
        """Test that URL is required."""
        with pytest.raises(ValidationError) as exc_info:
            ZenRowsUniversalScraperInput()
        assert "Field required" in str(exc_info.value)


class TestZenRowsUniversalScraper:
    """Test the ZenRows Universal Scraper tool."""

    def test_initialization_with_api_key(self):
        """Test successful initialization with API key."""
        scraper = ZenRowsUniversalScraper(zenrows_api_key="test-api-key")
        assert scraper.zenrows_api_key == "test-api-key"
        assert scraper.name == "zenrows_universal_scraper"
        assert scraper.base_url == "https://api.zenrows.com/v1/"

    @patch.dict(os.environ, {"ZENROWS_API_KEY": "env-api-key"})
    def test_initialization_with_env_variable(self):
        """Test initialization with environment variable."""
        scraper = ZenRowsUniversalScraper()
        assert scraper.zenrows_api_key == "env-api-key"

    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        with pytest.raises(ValueError) as exc_info:
            ZenRowsUniversalScraper()
        assert "ZenRows API key is required" in str(exc_info.value)

    def test_args_schema(self):
        """Test that args_schema is properly set."""
        scraper = ZenRowsUniversalScraper(zenrows_api_key="test-key")
        assert scraper.args_schema == ZenRowsUniversalScraperInput

    def test_description(self):
        """Test tool description is informative."""
        scraper = ZenRowsUniversalScraper(zenrows_api_key="test-key")
        description = scraper.description
        assert "web scraping" in description.lower()
        assert "javascript" in description.lower()
        assert "anti-bot" in description.lower()

    @patch("langchain_zenrows.zenrows_universal_scraper.requests.get")
    def test_run_success_html_response(self, mock_get):
        """Test successful _run method with HTML response."""
        # Setup mock response
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.content = b"<html><body>Test content</body></html>"
        mock_get.return_value = mock_response

        scraper = ZenRowsUniversalScraper(zenrows_api_key="test-key")

        result = scraper._run(url="https://example.com")

        assert result == "<html><body>Test content</body></html>"
        mock_get.assert_called_once()

        # Check the call arguments
        call_args = mock_get.call_args
        assert call_args[1]["params"]["url"] == "https://example.com"
        assert call_args[1]["params"]["apikey"] == "test-key"

    @patch("langchain_zenrows.zenrows_universal_scraper.requests.get")
    def test_run_with_all_parameters(self, mock_get):
        """Test _run method with all parameters."""
        # Setup mock response
        mock_response = Mock()
        mock_response.text = "Test content"
        mock_get.return_value = mock_response

        scraper = ZenRowsUniversalScraper(zenrows_api_key="test-key")

        css_extractor = json.dumps({"title": "h1"})

        result = scraper._run(
            url="https://example.com",
            js_render=True,
            js_instructions="window.scroll(0, 100);",
            premium_proxy=True,
            proxy_country="us",
            session_id=123,
            wait_for=".content",
            wait=2000,
            block_resources="images",
            response_type="markdown",
            css_extractor=css_extractor,
            autoparse=True,
        )

        assert result == "Test content"

        # Verify the API call
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["js_render"] is True
        assert params["premium_proxy"] is True
        assert params["proxy_country"] == "us"
        assert params["wait"] == 2000
        assert params["css_extractor"] == css_extractor

    def test_invoke_method(self):
        """Test invoke method (inherited from BaseTool)."""
        with patch.object(ZenRowsUniversalScraper, "_run") as mock_run:
            mock_run.return_value = "Invoked content"

            scraper = ZenRowsUniversalScraper(zenrows_api_key="test-key")
            result = scraper.invoke({"url": "https://example.com"})

            assert result == "Invoked content"
            mock_run.assert_called_once()

    def test_backward_compatibility_alias(self):
        """Test that ZenRowsUniversalScraperAPIWrapper is an alias."""
        assert ZenRowsUniversalScraperAPIWrapper is ZenRowsUniversalScraper

    def test_tool_metadata(self):
        """Test tool metadata and properties."""
        scraper = ZenRowsUniversalScraper(zenrows_api_key="test-key")

        # Test that it's a proper LangChain tool
        assert hasattr(scraper, "name")
        assert hasattr(scraper, "description")
        assert hasattr(scraper, "args_schema")
        assert hasattr(scraper, "_run")
        assert hasattr(scraper, "_arun")

        # Test specific properties
        assert scraper.name == "zenrows_universal_scraper"
        assert isinstance(scraper.description, str)
        assert len(scraper.description) > 50  # Should be descriptive
