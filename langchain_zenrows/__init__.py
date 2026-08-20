"""LangChain Zenrows integration package.

This package provides integration between LangChain and Zenrows Fetch API,
enabling powerful web scraping capabilities with anti-bot bypass, JavaScript
rendering, and geo-targeting features.
"""

from langchain_zenrows.zenrows_fetch import ZenrowsFetch, ZenrowsFetchInput

# Deprecated - kept for backward compatibility, redirect to the classes above.
from langchain_zenrows.zenrows_universal_scraper import (
    ZenRowsUniversalScraper,
    ZenRowsUniversalScraperAPIWrapper,
    ZenRowsUniversalScraperInput,
)

__version__ = "0.1.0"

__all__ = [
    "ZenrowsFetch",
    "ZenrowsFetchInput",
    # Deprecated aliases - use the names above instead.
    "ZenRowsUniversalScraper",
    "ZenRowsUniversalScraperAPIWrapper",
    "ZenRowsUniversalScraperInput",
]
