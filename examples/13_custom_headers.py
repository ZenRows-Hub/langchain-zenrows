"""
Scrape using custom headers.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper

# Set your ZenRows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Scrape with JavaScript rendering and premium proxies
result = scraper.invoke(
    {
        "url": "https://httpbin.io/headers",
        "js_render": True,
        "custom_headers": {"Referer": "https://google.com"},
    }
)

print(result)
