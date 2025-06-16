"""
Capture screenshots of specific page elements.
"""

import os
import base64
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Screenshot a specific element
result = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/ecommerce/",
        "screenshot_selector": "#product-list",
        "screenshot_format": "jpeg",
        "screenshot_quality": 85,
    }
)

# Save element screenshot
with open("products_grid_screenshot.jpg", "wb") as f:
    if isinstance(result, bytes):
        f.write(result)
    else:
        f.write(base64.b64decode(result))

print("Products grid screenshot saved as 'products_grid_screenshot.jpg'")
