"""
Capture full-page screenshots of websites.
"""

import os
import base64
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Capture full-page screenshot
result = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/ecommerce/",
        "js_render": True,
        "screenshot": "true",
        "screenshot_fullpage": "true",
    }
)

# Save screenshot to file
with open("full_page_screenshot.png", "wb") as f:
    if isinstance(result, bytes):
        f.write(result)
    else:
        f.write(base64.b64decode(result))

print("Full-page screenshot saved as 'full_page_screenshot.png'")
