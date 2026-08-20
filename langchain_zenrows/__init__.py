"""LangChain Zenrows integration package.

This package provides integration between LangChain and Zenrows Fetch and
Extract APIs, enabling powerful web scraping and AI-powered structured
extraction with anti-bot bypass, JavaScript rendering, and geo-targeting
features.
"""

from langchain_zenrows.zenrows_extract import ZenrowsExtract, ZenrowsExtractInput
from langchain_zenrows.zenrows_fetch import ZenrowsFetch, ZenrowsFetchInput

# Deprecated - kept for backward compatibility, redirect to the classes above.
from langchain_zenrows.zenrows_universal_scraper import (
    ZenRowsUniversalScraper,
    ZenRowsUniversalScraperAPIWrapper,
    ZenRowsUniversalScraperInput,
)

__version__ = "0.2.0"

__all__ = [
    "ZenrowsFetch",
    "ZenrowsFetchInput",
    "ZenrowsExtract",
    "ZenrowsExtractInput",
    # Deprecated aliases - use the names above instead.
    "ZenRowsUniversalScraper",
    "ZenRowsUniversalScraperAPIWrapper",
    "ZenRowsUniversalScraperInput",
]
