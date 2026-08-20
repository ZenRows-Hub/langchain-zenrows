"""
Capture JSON API calls made by web pages.
"""

import os
from langchain_zenrows import ZenrowsFetch

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenrowsFetch()

# Capture network requests and API calls
result = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/javascript-rendering",
        "json_response": True,
        "wait": 3000,  # Wait for API calls to complete
    }
)

print("Captured JSON API responses:")
print(result)
