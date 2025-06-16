# langchain-zenrows

The langchain-zenrows integration tool enables LangChain agents to scrape and access web content at any scale using ZenRows' enterprise-grade infrastructure. 

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

To use the ZenRows Universal Scraper with LangChain, you'll need a ZenRows API key. You can sign up for free at [ZenRows](https://app.zenrows.com/register?prod=universal_scraper).

> For more comprehensive examples and use cases, see the `examples/` folder.

### Basic Usage

```python
import os
from langchain_zenrows import ZenRowsUniversalScraper

# Set your ZenRows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

# Initialize the tool
scraper = ZenRowsUniversalScraper()

# Scrape a simple webpage
result = scraper.invoke({"url": "https://httpbin.io/html"})
print(result)
```

### Advanced Usage with Parameters

```python
import os
from langchain_zenrows import ZenRowsUniversalScraper

# Set your ZenRows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

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
from langchain_zenrows import ZenRowsUniversalScraper
from langchain_openai import ChatOpenAI  # or your preferred LLM
from langgraph.prebuilt import create_react_agent
import os

# Set your ZenRows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"
os.environ["OPENAI_API_KEY"] = "<YOUR_OPEN_AI_API_KEY>"


# Initialize components
llm = ChatOpenAI(model="gpt-4o-mini")
zenrows_tool = ZenRowsUniversalScraper()

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
from langchain_zenrows import ZenRowsUniversalScraper

# Set your ZenRows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

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
from langchain_zenrows import ZenRowsUniversalScraper

# Set your ZenRows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Check your IP location
result = scraper.invoke({
    "url": "https://httpbin.io/ip",
    "premium_proxy": True,
    "proxy_country": "us"
})
print(result)  # Shows the US IP being used
```

## API Reference

### ZenRowsUniversalScraper

Main tool class for web scraping with ZenRows.

**Parameters:**

- `zenrows_api_key` (str, optional): Your ZenRows API key. If not provided, looks for `ZENROWS_API_KEY` environment variable.

**Input Schema:**

For complete parameter documentation and details, see the [official ZenRows API Reference](https://docs.zenrows.com/universal-scraper-api/api-reference#parameter-overview).

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | str | **Required.** The URL to scrape |
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

## Features

- **JavaScript Rendering**: Scrape modern SPAs and dynamic content
- **Anti-Bot Bypass**: Bypass sophisticated bot detection systems
- **Geo-Targeting**: Access region-specific content with 190+ countries
- **Multiple Output Formats**: HTML, Markdown, Plaintext, PDF, Screenshots
- **CSS Extraction**: Target specific data with CSS selectors
- **Structured Data Extraction**: Automatically extract emails, phone numbers, links, and other data types
- **Session Management**: Maintain consistent sessions across requests
- **Wait Conditions**: Smart waiting for dynamic content
- **Premium Proxies**: 55M+ residential IPs for maximum success rates

## License

`langchain-zenrows` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Support

- [ZenRows Documentation](https://docs.zenrows.com/)
- [LangChain Documentation](https://python.langchain.com/)