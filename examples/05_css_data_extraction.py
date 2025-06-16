"""
Extract specific data using CSS selectors.
"""

import json
import os
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Define what data to extract using CSS selectors
css_selector = json.dumps(
    {
        "title": ".site-title",
        "product_names": ".product-name",
        "prices": ".product-price",
    }
)

result = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/ecommerce/",
        "js_render": True,
        "css_extractor": css_selector,
    }
)

print("Extracted product data:")
print(result)
