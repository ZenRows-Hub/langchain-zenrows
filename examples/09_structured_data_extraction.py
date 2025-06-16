"""
Automatically extract structured data like links, headings, etc.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Extract multiple data types automatically
result = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/ecommerce/",
        "outputs": "links,headings",
    }
)

print("Extracted structured data:")
print(result)
