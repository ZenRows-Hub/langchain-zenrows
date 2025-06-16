"""
Execute custom JavaScript to interact with page elements.
"""

import os
from langchain_zenrows import ZenRowsUniversalScraper

os.environ["ZENROWS_API_KEY"] = "<YOUR_ZENROWS_API_KEY>"

scraper = ZenRowsUniversalScraper()

result = scraper.invoke(
    {
        "url": "https://www.scrapingcourse.com/login",
        "js_instructions": """[{"fill":["#email","admin@example.com"]},
                            {"fill":["#password","password"]},
                            {"click":"#submit-button"},
                            {"wait":500}]""",
    }
)

print("Data extracted after JavaScript interactions:")
print(result)
