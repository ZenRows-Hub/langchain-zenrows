"""
Basic web scraping example demonstrating simple HTML extraction.
"""

import os
from langchain_zenrows import ZenrowsFetch

# Set your Zenrows API key
os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

# Initialize the scraper
scraper = ZenrowsFetch()

# Basic scraping
result = scraper.invoke({"url": "https://httpbin.io/html"})
print("Basic HTML content:")
print(result)
