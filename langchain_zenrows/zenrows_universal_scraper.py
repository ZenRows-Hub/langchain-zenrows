"""ZenRows Universal Scraper API integration for LangChain."""

import json
import os
from typing import Any, Dict, Literal, Optional, Type, Union

import requests
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, field_validator


class ZenRowsUniversalScraperInput(BaseModel):
    """Input schema for ZenRows Universal Scraper API."""

    url: str = Field(description="The URL of the page you want to scrape")
    js_render: Optional[bool] = Field(
        default=False,
        description="Enable JavaScript rendering with a headless browser. Essential for modern web apps, SPAs, and sites with dynamic content.",
    )
    js_instructions: Optional[str] = Field(
        default=None,
        description="Execute custom JavaScript on the page to interact with elements, scroll, click buttons, or manipulate content.",
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
    response_type: Optional[Literal["markdown", "plaintext", "pdf"]] = Field(
        default=None,
        description="Convert HTML to other formats. Options: markdown, plaintext, pdf.",
    )
    css_extractor: Optional[str] = Field(
        default=None,
        description="Extract specific elements using CSS selectors (JSON format).",
    )
    autoparse: Optional[bool] = Field(
        default=False, description="Automatically extract structured data from HTML."
    )
    screenshot: Optional[str] = Field(
        default=None, description="Capture an above-the-fold screenshot of the page."
    )
    screenshot_fullpage: Optional[str] = Field(
        default=None, description="Capture a full-page screenshot."
    )
    screenshot_selector: Optional[str] = Field(
        default=None,
        description="Capture a screenshot of a specific element using CSS Selector.",
    )
    original_status: Optional[bool] = Field(
        default=False,
        description="Return the original HTTP status code from the target page.",
    )
    allowed_status_codes: Optional[str] = Field(
        default=None,
        description="Returns the content even if the target page fails with specified status codes. Useful for debugging or when you need content from error pages.",
    )
    json_response: Optional[bool] = Field(
        default=False,
        description="Capture network requests in JSON format, including XHR or Fetch data. Ideal for intercepting API calls made by the web page.",
    )
    screenshot_format: Optional[Literal["png", "jpeg"]] = Field(
        default=None,
        description="Choose between png (default) and jpeg formats for screenshots.",
    )
    screenshot_quality: Optional[int] = Field(
        default=None,
        description="For JPEG format, set quality from 1 to 100. Lower values reduce file size but decrease quality.",
    )
    outputs: Optional[str] = Field(
        default=None,
        description="Specify which data types to extract from the scraped HTML. Accepted values: emails, phone_numbers, headings, images, audios, videos, links, menus, hashtags, metadata, tables, favicon.",
    )

    @field_validator("css_extractor")
    @classmethod
    def validate_css_extractor(cls, v):
        """Validate that css_extractor is valid JSON if provided."""
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("css_extractor must be valid JSON")
        return v

    @field_validator("proxy_country")
    @classmethod
    def validate_proxy_country(cls, v):
        """Validate that proxy_country is a two-letter country code."""
        if v is not None and len(v) != 2:
            raise ValueError("proxy_country must be a two-letter country code")
        return v


class ZenRowsUniversalScraper(BaseTool):
    """ZenRows Universal Scraper API tool for LangChain.

    This tool provides access to ZenRows' Universal Scraper API, enabling reliable
    web scraping with advanced features like JavaScript rendering, premium proxies,
    and anti-bot bypass.

    To use this tool, you must sign up for a ZenRows account and obtain an API key.
    Visit https://www.zenrows.com/ to get started.
    """

    name: str = "zenrows_universal_scraper"
    description: str = (
        "A powerful web scraping tool that can extract data from websites with "
        "anti-bot protection, JavaScript rendering, and geo-targeting capabilities. "
        "Use this when you need to scrape modern websites, bypass bot detection, "
        "or access geo-restricted content. Supports multiple output formats including "
        "HTML, Markdown, and screenshots."
    )
    args_schema: Type[BaseModel] = ZenRowsUniversalScraperInput

    zenrows_api_key: Optional[str] = None
    base_url: str = "https://api.zenrows.com/v1/"

    def __init__(self, zenrows_api_key: Optional[str] = None, **kwargs):
        """Initialize the ZenRows Universal Scraper tool.

        Args:
            zenrows_api_key: Your ZenRows API key. If not provided, will look for
                           ZENROWS_API_KEY environment variable.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.zenrows_api_key = zenrows_api_key or os.environ.get("ZENROWS_API_KEY")

        if not self.zenrows_api_key:
            raise ValueError(
                "ZenRows API key is required. Set ZENROWS_API_KEY environment "
                "variable or pass zenrows_api_key parameter."
            )

    def _prepare_request_params(
        self, tool_input: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare request parameters for the ZenRows API."""
        # Handle string input (just URL)
        if isinstance(tool_input, str):
            params = {"url": tool_input}
        else:
            params = tool_input.copy()

        # Auto-enable js_render for parameters that require JavaScript rendering
        js_required_params = [
            "screenshot",
            "screenshot_fullpage",
            "screenshot_selector",
            "js_instructions",
            "json_response",
            "wait",
            "wait_for",
        ]
        js_required = any(params.get(param) for param in js_required_params)

        if js_required:
            # If any parameter requiring JS is provided, enable js_render
            params["js_render"] = True

        # Special handling for screenshot variants
        screenshot_variants = ["screenshot_fullpage", "screenshot_selector"]
        if any(params.get(param) for param in screenshot_variants):
            # If screenshot_fullpage or screenshot_selector is provided,
            # also enable the base screenshot parameter
            params["screenshot"] = "true"

        # Auto-enable premium_proxy when proxy_country is specified
        if params.get("proxy_country"):
            params["premium_proxy"] = True

        # Add required API key
        params["apikey"] = self.zenrows_api_key

        # Handle custom headers according to ZenRows API documentation
        request_headers = None
        if "custom_headers" in params and params["custom_headers"]:
            # Store the headers dictionary for the request
            request_headers = params["custom_headers"]
            # Set custom_headers to "true" to enable custom header support in the API
            params["custom_headers"] = "true"
        else:
            # Remove custom_headers if not provided or empty
            params.pop("custom_headers", None)

        # Remove None values to avoid sending unnecessary parameters
        params = {k: v for k, v in params.items() if v is not None}

        return params, request_headers

    def _run(self, **kwargs) -> str:
        """Execute the ZenRows Universal Scraper API request.

        Returns:
            The scraped content as a string, format depends on response_type parameter.
        """
        try:
            params, request_headers = self._prepare_request_params(kwargs)

            # Make the API request
            # Note: ZenRows automatically handles User-Agent and other headers
            response = requests.get(
                self.base_url,
                params=params,
                headers=request_headers,  # Pass custom headers if provided
            )

            # Check for successful response
            response.raise_for_status()

            # Handle different response types
            screenshot_params = [
                "screenshot",
                "screenshot_fullpage",
                "screenshot_selector",
            ]
            if any(param in kwargs and kwargs[param] for param in screenshot_params):
                # For screenshots, return base64 encoded content with metadata
                return response.content

            # For text content, return the response text
            return response.text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid ZenRows API key")
            elif e.response.status_code == 429:
                raise ValueError("Rate limit exceeded. Check your ZenRows plan limits.")
            elif e.response.status_code == 413:
                raise ValueError(
                    "Response size too large. Consider using CSS selectors to reduce content."
                )
            else:
                raise ValueError(
                    f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
                )

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


# For backward compatibility and easier imports
ZenRowsUniversalScraperAPIWrapper = ZenRowsUniversalScraper
