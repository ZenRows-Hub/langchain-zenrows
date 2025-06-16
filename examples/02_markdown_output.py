"""
Scrape content in clean markdown format.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Get content in markdown format
result = scraper.invoke({"url": "https://www.example.com", "response_type": "markdown"})

print("Content in Markdown format:")
print(result)
