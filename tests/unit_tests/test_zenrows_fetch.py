"""Unit tests for Zenrows Fetch (the current, non-deprecated tool)."""

import json
import os
import warnings
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from langchain_zenrows import ZenrowsFetch, ZenrowsFetchInput


class TestZenrowsFetchInput:
    """Test the Pydantic input schema."""

    def test_minimal_valid_input(self):
        input_data = ZenrowsFetchInput(url="https://httpbin.io/html")
        assert input_data.url == "https://httpbin.io/html"
        assert input_data.js_render is None
        assert input_data.premium_proxy is None
        assert input_data.mode is None

    def test_invalid_css_extractor(self):
        with pytest.raises(ValidationError) as exc_info:
            ZenrowsFetchInput(url="https://example.com", css_extractor="invalid json")
        assert "css_extractor must be valid JSON" in str(exc_info.value)

    def test_invalid_proxy_country(self):
        with pytest.raises(ValidationError) as exc_info:
            ZenrowsFetchInput(url="https://example.com", proxy_country="usa")
        assert "proxy_country must be a two-letter country code" in str(exc_info.value)

    def test_mode_auto_accepted(self):
        input_data = ZenrowsFetchInput(url="https://example.com", mode="auto")
        assert input_data.mode == "auto"

    def test_mode_invalid_value_rejected(self):
        with pytest.raises(ValidationError):
            ZenrowsFetchInput(url="https://example.com", mode="not-a-mode")


class TestZenrowsFetch:
    """Test the Zenrows Fetch tool."""

    def test_initialization_with_api_key(self):
        scraper = ZenrowsFetch(zenrows_api_key="test-api-key")
        assert scraper.zenrows_api_key == "test-api-key"
        assert scraper.name == "zenrows_fetch"
        assert scraper.base_url == "https://api.zenrows.com/v1/"

    @patch.dict(os.environ, {"ZENROWS_API_KEY": "env-api-key"})
    def test_initialization_with_env_variable(self):
        scraper = ZenrowsFetch()
        assert scraper.zenrows_api_key == "env-api-key"

    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_api_key(self):
        with pytest.raises(ValueError) as exc_info:
            ZenrowsFetch()
        assert "Zenrows API key is required" in str(exc_info.value)

    def test_args_schema(self):
        scraper = ZenrowsFetch(zenrows_api_key="test-key")
        assert scraper.args_schema == ZenrowsFetchInput

    def test_no_deprecation_warning(self):
        """ZenrowsFetch is the current class - instantiating it must not warn,
        unlike its deprecated ZenRowsUniversalScraper redirect."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            ZenrowsFetch(zenrows_api_key="test-key")

    @patch("langchain_zenrows.zenrows_fetch.requests.get")
    def test_run_success_html_response(self, mock_get):
        mock_response = Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.content = b"<html><body>Test content</body></html>"
        mock_get.return_value = mock_response

        scraper = ZenrowsFetch(zenrows_api_key="test-key")
        result = scraper._run(url="https://example.com")

        assert result == "<html><body>Test content</body></html>"
        call_args = mock_get.call_args
        assert call_args[1]["params"]["url"] == "https://example.com"
        assert call_args[1]["params"]["apikey"] == "test-key"

    @patch("langchain_zenrows.zenrows_fetch.requests.get")
    def test_run_with_all_parameters(self, mock_get):
        mock_response = Mock()
        mock_response.text = "Test content"
        mock_get.return_value = mock_response

        scraper = ZenrowsFetch(zenrows_api_key="test-key")
        css_extractor = json.dumps({"title": "h1"})

        result = scraper._run(
            url="https://example.com",
            js_render=True,
            premium_proxy=True,
            proxy_country="us",
            wait=2000,
            css_extractor=css_extractor,
        )

        assert result == "Test content"
        params = mock_get.call_args[1]["params"]
        assert params["js_render"] is True
        assert params["premium_proxy"] is True
        assert params["proxy_country"] == "us"
        assert params["wait"] == 2000
        assert params["css_extractor"] == css_extractor

    def test_invoke_method(self):
        with patch.object(ZenrowsFetch, "_run") as mock_run:
            mock_run.return_value = "Invoked content"
            scraper = ZenrowsFetch(zenrows_api_key="test-key")
            result = scraper.invoke({"url": "https://example.com"})
            assert result == "Invoked content"
            mock_run.assert_called_once()


@patch("langchain_zenrows.zenrows_fetch.requests.get")
class TestAdaptiveStealthMode:
    """Adaptive Stealth Mode (mode="auto") - Zenrows manages js_render/premium_proxy
    itself, so the client-side auto-enable heuristics must stay out of its way."""

    BASE_URL = "https://example.com"

    def setup_method(self):
        self.scraper = ZenrowsFetch(zenrows_api_key="test-key")

    def _scrape(self, mock_get, **kwargs) -> dict:
        mock_get.return_value = Mock(text="<html>content</html>", content=b"\x89PNG...")
        self.scraper._run(url=self.BASE_URL, **kwargs)
        return mock_get.call_args[1]["params"]

    def test_mode_auto_sent_as_query_param(self, mock_get):
        params = self._scrape(mock_get, mode="auto")
        assert params["mode"] == "auto"

    def test_mode_auto_does_not_force_js_render(self, mock_get):
        # wait_for normally forces js_render=True, but not in mode=auto
        params = self._scrape(mock_get, mode="auto", wait_for=".content")
        assert "js_render" not in params
        assert params["mode"] == "auto"

    def test_mode_auto_does_not_force_premium_proxy(self, mock_get):
        # proxy_country normally forces premium_proxy=True, but not in mode=auto
        params = self._scrape(mock_get, mode="auto", proxy_country="us")
        assert "premium_proxy" not in params
        assert params["proxy_country"] == "us"
        assert params["mode"] == "auto"

    def test_mode_auto_compatible_with_js_instructions(self, mock_get):
        params = self._scrape(mock_get, mode="auto", js_instructions='[{"scroll_y": 500}]')
        assert params["mode"] == "auto"
        assert params["js_instructions"] == '[{"scroll_y": 500}]'

    def test_without_mode_auto_js_render_still_forced(self, mock_get):
        params = self._scrape(mock_get, wait_for=".content")
        assert params["js_render"] is True

    def test_mode_auto_still_injects_screenshot_base_param(self, mock_get):
        params = self._scrape(mock_get, mode="auto", screenshot_fullpage="true")
        assert params["mode"] == "auto"
        assert params["screenshot_fullpage"] == "true"
        assert params["screenshot"] == "true"
