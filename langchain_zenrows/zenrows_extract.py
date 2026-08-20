"""Zenrows Extract integration for LangChain.

Extract uses the same endpoint as Fetch (`https://api.zenrows.com/v1/`)
with `extract` set - it is not a separate API. When `extract` is set, the
server ignores `autoparse`, `css_extractor`, `response_type`, and `outputs`
on that request, so this tool's input schema deliberately omits them rather
than accept params that would silently do nothing.

See https://docs.zenrows.com/extract/setup for the current contract.
"""

import json
import os
from typing import Any, Dict, Literal, Optional, Type, Union

import requests
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, field_validator


class ZenrowsExtractInput(BaseModel):
    """Input schema for Zenrows Extract."""

    url: str = Field(description="The URL of the page you want to extract data from")
    extract: Literal["auto", "native", "standard"] = Field(
        default="auto",
        description="Extraction mode. 'auto' (default) lets Zenrows detect the page type and structure the data automatically.",
    )
    js_render: Optional[bool] = Field(
        default=False,
        description="Enable JavaScript rendering with a headless browser. Essential for modern web apps, SPAs, and sites with dynamic content.",
    )
    premium_proxy: Optional[bool] = Field(
        default=False,
        description="Use residential IPs to bypass anti-bot protection. Essential for accessing protected sites.",
    )
    proxy_country: Optional[str] = Field(
        default=None,
        description="Set the country of the IP used for the request (requires Premium Proxies). Use for accessing geo-restricted content.",
    )
    session_id: Optional[int] = Field(
        default=None,
        description="Maintain the same IP for multiple requests for up to 10 minutes. Essential for multi-step processes.",
    )
    custom_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Include custom headers in your request to mimic browser behavior.",
    )
    wait_for: Optional[str] = Field(
        default=None,
        description="Wait for a specific CSS Selector to appear in the DOM before returning content.",
    )
    wait: Optional[int] = Field(
        default=None, description="Wait a fixed amount of milliseconds after page load."
    )
    block_resources: Optional[str] = Field(
        default=None,
        description="Block specific resources (images, fonts, etc.) from loading to speed up scraping.",
    )
    original_status: Optional[bool] = Field(
        default=False,
        description="Return the original HTTP status code from the target page.",
    )
    allowed_status_codes: Optional[str] = Field(
        default=None,
        description="Returns the content even if the target page fails with specified status codes. Useful for debugging or when you need content from error pages.",
    )
    fallback_to_autoparse: bool = Field(
        default=True,
        description="When extract='auto' hits a domain not yet enabled for the Extract beta, automatically retry once with the general-purpose Autoparse feature instead of raising. Set False to disable and always raise on that error.",
    )

    @field_validator("proxy_country")
    @classmethod
    def validate_proxy_country(cls, v):
        """Validate that proxy_country is a two-letter country code."""
        if v is not None and len(v) != 2:
            raise ValueError("proxy_country must be a two-letter country code")
        return v


class ZenrowsExtract(BaseTool):
    """Zenrows Extract tool for LangChain.

    This tool provides access to Zenrows' Extract API (beta) - AI-powered
    structured extraction. Unlike `ZenrowsFetch`, it always returns
    `application/json` with a `parsed` field (the structured data) and an
    `html` field (the raw page HTML, included during beta for validation).
    The result is returned as the raw JSON text; parse it with `json.loads()`
    if you need the structured fields directly.

    To use this tool, you must sign up for a Zenrows account and obtain an
    API key. Visit https://www.zenrows.com/ to get started.
    """

    name: str = "zenrows_extract"
    description: str = (
        "Extract structured, AI-parsed data from a webpage - product details, "
        "listings, articles, and similar content - without writing CSS selectors. "
        "Returns JSON with a 'parsed' field (the structured data) and an 'html' "
        "field (the raw page HTML). Use this instead of the plain scraping tool "
        "when you want structured fields rather than raw HTML/Markdown."
    )
    args_schema: Type[BaseModel] = ZenrowsExtractInput

    zenrows_api_key: Optional[str] = None
    base_url: str = "https://api.zenrows.com/v1/"

    def __init__(self, zenrows_api_key: Optional[str] = None, **kwargs):
        """Initialize the Zenrows Extract tool.

        Args:
            zenrows_api_key: Your Zenrows API key. If not provided, will look for
                           ZENROWS_API_KEY environment variable.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.zenrows_api_key = zenrows_api_key or os.environ.get("ZENROWS_API_KEY")

        if not self.zenrows_api_key:
            raise ValueError(
                "Zenrows API key is required. Set ZENROWS_API_KEY environment "
                "variable or pass zenrows_api_key parameter."
            )

    def _prepare_request_params(
        self,
        tool_input: Union[str, Dict[str, Any]],
        *,
        autoparse_fallback: bool = False,
    ) -> Dict[str, Any]:
        """Prepare request parameters for the Zenrows API.

        With ``autoparse_fallback=True``, build an Autoparse request instead
        of an Extract one - same target URL and knobs, minus the
        extract-specific bits Autoparse doesn't take.
        """
        if isinstance(tool_input, str):
            params: Dict[str, Any] = {"url": tool_input}
        else:
            params = tool_input.copy()

        # Local control flag, never sent on the wire.
        params.pop("fallback_to_autoparse", None)

        if autoparse_fallback:
            params.pop("extract", None)
            params["autoparse"] = True
        else:
            # extract=auto is the whole point of this tool - always set,
            # defaulting to "auto" if the caller didn't specify a mode.
            params["extract"] = params.get("extract") or "auto"

        if params.get("wait_for") or params.get("wait"):
            params["js_render"] = True

        if params.get("proxy_country"):
            params["premium_proxy"] = True

        params["apikey"] = self.zenrows_api_key

        request_headers = None
        if "custom_headers" in params and params["custom_headers"]:
            request_headers = params["custom_headers"]
            params["custom_headers"] = "true"
        else:
            params.pop("custom_headers", None)

        params = {k: v for k, v in params.items() if v is not None}

        return params, request_headers

    @staticmethod
    def _error_code(body: str) -> Optional[str]:
        """Pull the Zenrows JSON error envelope's `code` field, if any -
        mirrors the CLI's `zrErrorCode` helper. Returns None on non-JSON or
        missing/non-string `code`."""
        try:
            parsed = json.loads(body)
        except (ValueError, TypeError):
            return None
        code = parsed.get("code") if isinstance(parsed, dict) else None
        return code.upper() if isinstance(code, str) else None

    def _send(self, params: Dict[str, Any], request_headers: Optional[Dict[str, str]]):
        """Issue the request. Raises `requests.exceptions.HTTPError` (with the
        response attached) on non-2xx, same as `Response.raise_for_status()`."""
        response = requests.get(self.base_url, params=params, headers=request_headers)
        response.raise_for_status()
        return response

    def _raise_for_http_error(self, e: requests.exceptions.HTTPError) -> None:
        if e.response.status_code == 401:
            raise ValueError("Invalid Zenrows API key")
        elif e.response.status_code == 429:
            raise ValueError("Rate limit exceeded. Check your Zenrows plan limits.")
        elif e.response.status_code == 413:
            raise ValueError(
                "Response size too large. Consider using CSS selectors to reduce content."
            )
        else:
            raise ValueError(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )

    def _run_autoparse_fallback(self, kwargs: Dict[str, Any]) -> str:
        """Retry with Autoparse and re-wrap the result into Extract's
        ``{"parsed", "html"}`` envelope, so callers can rely on `data["parsed"]`
        either way. Adds `extract_fallback: "autoparse"` so callers/agents can
        tell a fallback happened rather than a real Extract response."""
        params, request_headers = self._prepare_request_params(
            kwargs, autoparse_fallback=True
        )
        response = self._send(params, request_headers)

        try:
            parsed_data: Any = response.json()
        except ValueError:
            parsed_data = response.text

        return json.dumps(
            {"parsed": parsed_data, "html": None, "extract_fallback": "autoparse"}
        )

    def _run(self, **kwargs) -> str:
        """Execute the Zenrows Extract request.

        When `extract` is "auto" (the default) and the target domain isn't
        yet enabled for the Extract beta - the API's `AUTH010` error - this
        automatically retries once with Autoparse instead of raising, same
        as the CLI's default behavior. Pass `fallback_to_autoparse=False` to
        disable that and always raise on `AUTH010`.

        Returns:
            The raw JSON response text. On a normal Extract response this is
            a dict with `parsed` and `html` fields; on an Autoparse fallback
            it's re-wrapped into that same shape, plus
            `extract_fallback: "autoparse"` so callers can tell which path
            was taken. Use `json.loads()` on the result either way.
        """
        fallback_enabled = kwargs.get("fallback_to_autoparse", True)
        mode = kwargs.get("extract") or "auto"

        try:
            params, request_headers = self._prepare_request_params(kwargs)
            response = self._send(params, request_headers)
            return response.text

        except requests.exceptions.HTTPError as e:
            if (
                e.response.status_code == 402
                and mode == "auto"
                and fallback_enabled
                and self._error_code(e.response.text) == "AUTH010"
            ):
                try:
                    return self._run_autoparse_fallback(kwargs)
                except requests.exceptions.HTTPError as fallback_error:
                    self._raise_for_http_error(fallback_error)
            self._raise_for_http_error(e)

        except requests.exceptions.Timeout:
            raise ValueError(
                "Request timed out. The website might be slow or unresponsive."
            )

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request failed: {str(e)}")

        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")

    async def _arun(self, **kwargs) -> str:
        """Async version of _run method."""
        return self._run(**kwargs)
