"""
Access geo-restricted content using premium proxies.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

# Access content from a specific country
result = scraper.invoke(
    {"url": "https://httpbin.io/ip", "premium_proxy": True, "proxy_country": "us"}
)

print("Request from US IP:")
print(result)

# Try from different country
result_uk = scraper.invoke(
    {"url": "https://httpbin.io/ip", "premium_proxy": True, "proxy_country": "gb"}
)

print("Request from UK IP:")
print(result_uk)
