"""
Scrape modern Single Page Applications with JavaScript rendering.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Scrape SPA with JavaScript rendering and wait for content
result = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/javascript-rendering",
        "js_render": True,
        "wait": 3000,  # Wait 3 seconds for content to load
        "wait_for": ".product-name",  # Wait for specific element
        "response_type": "markdown",
    }
)

print("SPA content (rendered with JavaScript):")
print(result)
