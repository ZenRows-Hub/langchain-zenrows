"""Unit tests for Zenrows Extract."""

import json
import os
from unittest.mock import Mock, patch

import pytest
import requests
from pydantic import ValidationError

from langchain_zenrows import ZenrowsExtract, ZenrowsExtractInput


def _http_error(status_code: int, body: str) -> requests.exceptions.HTTPError:
    """Build an HTTPError carrying a fake response, matching what
    `Response.raise_for_status()` raises."""
    response = Mock()
    response.status_code = status_code
    response.text = body
    return requests.exceptions.HTTPError(response=response)


class TestZenrowsExtractInput:
    """Test the Pydantic input schema."""

    def test_minimal_valid_input_defaults_to_auto(self):
        input_data = ZenrowsExtractInput(url="https://example.com")
        assert input_data.url == "https://example.com"
        assert input_data.extract == "auto"

    def test_explicit_mode(self):
        input_data = ZenrowsExtractInput(url="https://example.com", extract="native")
        assert input_data.extract == "native"

    def test_invalid_mode_rejected(self):
        with pytest.raises(ValidationError):
            ZenrowsExtractInput(url="https://example.com", extract="not-a-real-mode")

    def test_invalid_proxy_country(self):
        with pytest.raises(ValidationError) as exc_info:
            ZenrowsExtractInput(url="https://example.com", proxy_country="usa")
        assert "proxy_country must be a two-letter country code" in str(exc_info.value)

    def test_no_autoparse_or_css_extractor_fields(self):
        """extract=auto ignores these on the server, so the schema shouldn't
        offer them - offering a param that silently does nothing is worse
        than not offering it."""
        fields = ZenrowsExtractInput.model_fields
        assert "autoparse" not in fields
        assert "css_extractor" not in fields
        assert "response_type" not in fields
        assert "outputs" not in fields


class TestZenrowsExtract:
    """Test the Zenrows Extract tool."""

    def test_initialization_with_api_key(self):
        tool = ZenrowsExtract(zenrows_api_key="test-api-key")
        assert tool.zenrows_api_key == "test-api-key"
        assert tool.name == "zenrows_extract"
        assert tool.base_url == "https://api.zenrows.com/v1/"

    @patch.dict(os.environ, {"ZENROWS_API_KEY": "env-api-key"})
    def test_initialization_with_env_variable(self):
        tool = ZenrowsExtract()
        assert tool.zenrows_api_key == "env-api-key"

    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_api_key(self):
        with pytest.raises(ValueError) as exc_info:
            ZenrowsExtract()
        assert "Zenrows API key is required" in str(exc_info.value)

    def test_args_schema(self):
        tool = ZenrowsExtract(zenrows_api_key="test-key")
        assert tool.args_schema == ZenrowsExtractInput

    @patch("langchain_zenrows.zenrows_extract.requests.get")
    def test_run_defaults_extract_to_auto(self, mock_get):
        mock_response = Mock()
        mock_response.text = '{"parsed": {"name": "Widget"}, "html": "<html></html>"}'
        mock_get.return_value = mock_response

        tool = ZenrowsExtract(zenrows_api_key="test-key")
        result = tool._run(url="https://example.com")

        assert result == '{"parsed": {"name": "Widget"}, "html": "<html></html>"}'
        params = mock_get.call_args[1]["params"]
        assert params["url"] == "https://example.com"
        assert params["extract"] == "auto"
        assert params["apikey"] == "test-key"

    @patch("langchain_zenrows.zenrows_extract.requests.get")
    def test_run_with_explicit_mode(self, mock_get):
        mock_response = Mock()
        mock_response.text = "{}"
        mock_get.return_value = mock_response

        tool = ZenrowsExtract(zenrows_api_key="test-key")
        tool._run(url="https://example.com", extract="standard")

        params = mock_get.call_args[1]["params"]
        assert params["extract"] == "standard"

    @patch("langchain_zenrows.zenrows_extract.requests.get")
    def test_proxy_country_auto_enables_premium_proxy(self, mock_get):
        mock_response = Mock()
        mock_response.text = "{}"
        mock_get.return_value = mock_response

        tool = ZenrowsExtract(zenrows_api_key="test-key")
        tool._run(url="https://example.com", proxy_country="us")

        params = mock_get.call_args[1]["params"]
        assert params["premium_proxy"] is True

    def test_invoke_method(self):
        with patch.object(ZenrowsExtract, "_run") as mock_run:
            mock_run.return_value = '{"parsed": {}}'
            tool = ZenrowsExtract(zenrows_api_key="test-key")
            result = tool.invoke({"url": "https://example.com"})
            assert result == '{"parsed": {}}'
            mock_run.assert_called_once()


class TestExtractAutoparseFallback:
    """AUTH010 (domain not enabled for Extract beta) -> retry with Autoparse,
    same behavior as the CLI's extract adapter."""

    @patch("langchain_zenrows.zenrows_extract.requests.get")
    def test_falls_back_to_autoparse_on_auth010(self, mock_get):
        first_response = Mock()
        first_response.raise_for_status.side_effect = _http_error(
            402, '{"code": "AUTH010", "title": "Domain not enabled for Extract"}'
        )

        second_response = Mock()
        second_response.raise_for_status.return_value = None
        second_response.text = '{"title": "Widget", "price": "9.99"}'
        second_response.json.return_value = {"title": "Widget", "price": "9.99"}

        mock_get.side_effect = [first_response, second_response]

        tool = ZenrowsExtract(zenrows_api_key="test-key")
        result = tool._run(url="https://example.com")

        data = json.loads(result)
        assert data["extract_fallback"] == "autoparse"
        assert data["parsed"] == {"title": "Widget", "price": "9.99"}
        assert data["html"] is None

        assert mock_get.call_count == 2
        fallback_params = mock_get.call_args_list[1][1]["params"]
        assert fallback_params.get("autoparse") is True
        assert "extract" not in fallback_params

    @patch("langchain_zenrows.zenrows_extract.requests.get")
    def test_fallback_disabled_raises_instead(self, mock_get):
        response = Mock()
        response.raise_for_status.side_effect = _http_error(
            402, '{"code": "AUTH010"}'
        )
        mock_get.return_value = response

        tool = ZenrowsExtract(zenrows_api_key="test-key")
        with pytest.raises(ValueError):
            tool._run(url="https://example.com", fallback_to_autoparse=False)

        # No fallback attempt made.
        assert mock_get.call_count == 1

    @patch("langchain_zenrows.zenrows_extract.requests.get")
    def test_402_without_auth010_does_not_fall_back(self, mock_get):
        """A real credits-exhausted 402 (e.g. AUTH004) must raise normally,
        not be mistaken for the domain-gating error."""
        response = Mock()
        response.raise_for_status.side_effect = _http_error(
            402, '{"code": "AUTH004", "title": "No credit available"}'
        )
        mock_get.return_value = response

        tool = ZenrowsExtract(zenrows_api_key="test-key")
        with pytest.raises(ValueError, match="HTTP error occurred: 402"):
            tool._run(url="https://example.com")

        assert mock_get.call_count == 1

    @patch("langchain_zenrows.zenrows_extract.requests.get")
    def test_no_fallback_for_non_auto_mode(self, mock_get):
        """AUTH010 shouldn't apply to native/standard modes - only auto is
        the domain-gated beta path."""
        response = Mock()
        response.raise_for_status.side_effect = _http_error(
            402, '{"code": "AUTH010"}'
        )
        mock_get.return_value = response

        tool = ZenrowsExtract(zenrows_api_key="test-key")
        with pytest.raises(ValueError):
            tool._run(url="https://example.com", extract="native")

        assert mock_get.call_count == 1
