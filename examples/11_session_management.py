"""
Maintain consistent sessions across multiple requests.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

session_id = 12345  # Use same session for related requests

# Step 1: Login or initial page
result1 = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/login",
        "premium_proxy": True,
        "session_id": session_id,
        "js_instructions": """[{"fill":["#email","admin@example.com"]},
                            {"fill":["#password","password"]},
                            {"click":"#submit-button"},
                            {"wait":500}]""",
    }
)

# Step 2: Access protected content with same session
result2 = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/dashboard",
        "premium_proxy": True,
        "session_id": session_id,
    }
)

print("First request (login page):")
print(result1[:200] + "...")

print("\nSecond request (dashboard with same session):")
print(result2[:200] + "...")
