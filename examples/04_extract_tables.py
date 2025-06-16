"""
Extract all tables from a webpage using structured data extraction.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Extract all tables from the page
result = scraper.invoke(
    {"url": "https://www.scrapingcourse.com/table-parsing", "outputs": "tables"}
)

print("Extracted tables:")
print(result)
