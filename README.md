# langchain-zenrows

The langchain-zenrows integration tool enables LangChain agents to scrape and access web content at any scale using Zenrows' enterprise-grade infrastructure. 

Whether you need to scrape JavaScript-heavy single-page applications, bypass anti-bot systems, access geo-restricted content, or extract structured data at scale, this integration provides the tools and reliability needed for modern AI applications.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Features](#features)
- [License](#license)

## Installation

```console
pip install langchain-zenrows
```

## Usage

To use the Zenrows Fetch with LangChain, you'll need a Zenrows API key. You can sign up for free at [Zenrows](https://app.zenrows.com/register?prod=fetch).

> For more comprehensive examples and use cases, see the `examples/` folder.

> **Renamed:** this tool was previously exported as `ZenRowsUniversalScraper`. That name still works (it's a deprecated alias that redirects to `ZenrowsFetch` and will keep working until removed in a future release), but new code should import `ZenrowsFetch`.

### Basic Usage

```python
import os
from langchain_zenrows import ZenrowsFetch

# Set your Zenrows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

# Initialize the tool
scraper = ZenrowsFetch()

# Scrape a simple webpage
result = scraper.invoke({"url": "https://httpbin.io/html"})
print(result)
```

### Advanced Usage with Parameters

```python
import os
from langchain_zenrows import ZenrowsFetch

# Set your Zenrows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenrowsFetch()

# Scrape with JavaScript rendering and premium proxies
result = scraper.invoke({
    "url": "https://www.scrapingcourse.com/ecommerce/",
    "js_render": True,
    "premium_proxy": True,
    "proxy_country": "us",
    "response_type": "markdown",
    "wait": 2000  # Wait 2 seconds after page load
})

print(result)
```

See the [API Reference](#api-reference) section below for more available parameters and customizing scraping requests.

### Using with LangChain Agents

```python
from langchain_zenrows import ZenrowsFetch
from langchain_openai import ChatOpenAI  # or your preferred LLM
from langgraph.prebuilt import create_react_agent
import os

# Set your Zenrows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"
os.environ["OPENAI_API_KEY"] = "<YOUR_OPEN_AI_API_KEY>"


# Initialize components
llm = ChatOpenAI(model="gpt-4o-mini")
zenrows_tool = ZenrowsFetch()

# Create agent
agent = create_react_agent(llm, [zenrows_tool])

# Use the agent
result = agent.invoke(
    {
        "messages": "Scrape https://news.ycombinator.com/ and list the top 3 stories with title, points, comments, username, and time."
    }
)

print("Agent Response:")
for message in result["messages"]:
    print(f"{message.content}")
```

### CSS Extraction

Extract specific data using CSS selectors:

```python
import json
import os
from langchain_zenrows import ZenrowsFetch

# Set your Zenrows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenrowsFetch()

# Extract specific elements
css_selector = json.dumps({
    "title": "h1",
    "paragraphs": "p"
})

result = scraper.invoke({
    "url": "https://httpbin.io/html",
    "css_extractor": css_selector
})
```

### Premium Proxy with Geo-targeting

Access geo-restricted content:

```python
import os
from langchain_zenrows import ZenrowsFetch

# Set your Zenrows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenrowsFetch()

# Check your IP location
result = scraper.invoke({
    "url": "https://httpbin.io/ip",
    "premium_proxy": True,
    "proxy_country": "us"
})
print(result)  # Shows the US IP being used
```

### Extract - structured data without CSS selectors

`ZenrowsExtract` uses AI to return structured data instead of raw HTML. It's a
separate tool from `ZenrowsFetch` with its own, leaner input schema - options
that Fetch supports but Extract's server ignores (`autoparse`, `css_extractor`,
`response_type`, `outputs`) aren't offered here at all, so there's nothing to
set that silently does nothing. The result is JSON with `parsed` (the
structured data) and `html` (the raw page, included during beta):

```python
import json
import os
from langchain_zenrows import ZenrowsExtract

# Set your Zenrows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

extractor = ZenrowsExtract()

result = extractor.invoke({"url": "https://www.scrapingcourse.com/ecommerce/"})
data = json.loads(result)
print(data["parsed"])
```

See the [Extract docs](https://docs.zenrows.com/extract/setup) for details on
what `parsed` looks like for different page types.

**Autoparse fallback:** `extract="auto"` (the default) is a domain-gated open
beta - if the target site isn't enabled yet, Zenrows returns an `AUTH010`
error. By default, `ZenrowsExtract` catches that and retries once with the
general-purpose Autoparse feature instead of raising, matching the CLI's
`zenrows extract` behavior. The result is re-wrapped into the same
`{"parsed": ..., "html": ...}` shape, plus `extract_fallback: "autoparse"` so
you can tell a fallback happened:

```python
data = json.loads(result)
if data.get("extract_fallback"):
    print("This domain isn't in the Extract beta yet - used Autoparse instead.")
print(data["parsed"])
```

Pass `fallback_to_autoparse=False` to disable this and always raise on
`AUTH010` instead.

## API Reference

### ZenrowsFetch

Main tool class for web scraping with Zenrows.

**Parameters:**

- `zenrows_api_key` (str, optional): Your Zenrows API key. If not provided, looks for `ZENROWS_API_KEY` environment variable.

**Input Schema:**

For complete parameter documentation and details, see the [official Zenrows API Reference](https://docs.zenrows.com/fetch/api-reference#parameter-overview).

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | str | **Required.** The URL to scrape |
| `mode` | str | Set to `"auto"` to enable Adaptive Stealth Mode — Zenrows starts with the cheapest viable setup and escalates to `js_render`/`premium_proxy` only when needed, billing only for the configuration that succeeds. When set, `js_render` and `premium_proxy` aren't auto-enabled by this tool's own heuristics (Zenrows manages them) |
| `js_render` | bool | Enable JavaScript rendering with a headless browser. Essential for modern web apps, SPAs, and sites with dynamic content (default: False) |
| `js_instructions` | str | Execute custom JavaScript on the page to interact with elements, scroll, click buttons, or manipulate content |
| `premium_proxy` | bool | Use residential IPs to bypass anti-bot protection. Essential for accessing protected sites (default: False) |
| `proxy_country` | str | Set the country of the IP used for the request. Use for accessing geo-restricted content. Two-letter country code |
| `session_id` | int | Maintain the same IP for multiple requests for up to 10 minutes. Essential for multi-step processes |
| `custom_headers` | dict | Include custom headers in your request to mimic browser behavior |
| `wait_for` | str | Wait for a specific CSS Selector to appear in the DOM before returning content |
| `wait` | int | Wait a fixed amount of milliseconds after page load |
| `block_resources` | str | Block specific resources (images, fonts, etc.) from loading to speed up scraping |
| `response_type` | str | Convert HTML to other formats. Options: "markdown", "plaintext", "pdf" |
| `css_extractor` | str | Extract specific elements using CSS selectors (JSON format) |
| `autoparse` | bool | Automatically extract structured data from HTML (default: False) |
| `screenshot` | str | Capture an above-the-fold screenshot of the page (default: "false") |
| `screenshot_fullpage` | str | Capture a full-page screenshot (default: "false") |
| `screenshot_selector` | str | Capture a screenshot of a specific element using CSS Selector |
| `screenshot_format` | str | Choose between "png" (default) and "jpeg" formats for screenshots |
| `screenshot_quality` | int | For JPEG format, set quality from 1 to 100. Lower values reduce file size but decrease quality |
| `original_status` | bool | Return the original HTTP status code from the target page (default: False) |
| `allowed_status_codes` | str | Returns the content even if the target page fails with specified status codes. Useful for debugging or when you need content from error pages |
| `json_response` | bool | Capture network requests in JSON format, including XHR or Fetch data. Ideal for intercepting API calls made by the web page (default: False) |
| `outputs` | str | Specify which data types to extract from the scraped HTML. Accepted values: emails, phone_numbers, headings, images, audios, videos, links, menus, hashtags, metadata, tables, favicon |

### ZenrowsExtract

Tool class for AI-powered structured extraction (beta). Same `zenrows_api_key` parameter as `ZenrowsFetch`. Returns JSON (`parsed` + `html`) instead of raw HTML/Markdown.

For complete details, see the [official Extract docs](https://docs.zenrows.com/extract/setup).

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | str | **Required.** The URL to extract data from |
| `extract` | str | Extraction mode: "auto" (default), "native", or "standard" |
| `js_render` | bool | Enable JavaScript rendering with a headless browser (default: False) |
| `premium_proxy` | bool | Use residential IPs to bypass anti-bot protection (default: False) |
| `proxy_country` | str | Two-letter country code for the request's IP (requires Premium Proxies) |
| `session_id` | int | Maintain the same IP for multiple requests for up to 10 minutes |
| `custom_headers` | dict | Include custom headers in your request |
| `wait_for` | str | Wait for a specific CSS Selector to appear before returning content |
| `wait` | int | Wait a fixed amount of milliseconds after page load |
| `block_resources` | str | Block specific resources (images, fonts, etc.) from loading |
| `original_status` | bool | Return the original HTTP status code from the target page (default: False) |
| `allowed_status_codes` | str | Return content even if the target page fails with the specified status codes |
| `fallback_to_autoparse` | bool | Retry once with Autoparse if `extract="auto"` hits a domain not yet enabled for the Extract beta (default: True) |

Not offered here - the server ignores these when `extract` is set, so they aren't in this schema: `autoparse`, `css_extractor`, `response_type`, `outputs`.

## Features

- **JavaScript Rendering**: Scrape modern SPAs and dynamic content
- **Anti-Bot Bypass**: Bypass sophisticated bot detection systems
- **Geo-Targeting**: Access region-specific content with 190+ countries
- **Multiple Output Formats**: HTML, Markdown, Plaintext, PDF, Screenshots
- **CSS Extraction**: Target specific data with CSS selectors
- **AI-Powered Extraction (beta)**: Structured data without writing selectors, via `ZenrowsExtract`
- **Structured Data Extraction**: Automatically extract emails, phone numbers, links, and other data types
- **Session Management**: Maintain consistent sessions across requests
- **Wait Conditions**: Smart waiting for dynamic content
- **Premium Proxies**: 55M+ residential IPs for maximum success rates

## License

`langchain-zenrows` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Support

- [Zenrows Documentation](https://docs.zenrows.com/)
- [LangChain Documentation](https://python.langchain.com/)