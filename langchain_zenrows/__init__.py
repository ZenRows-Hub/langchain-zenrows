"""LangChain ZenRows integration package.

This package provides integration between LangChain and ZenRows Universal Scraper API,
enabling powerful web scraping capabilities with anti-bot bypass, JavaScript
rendering, and geo-targeting features.
"""

from langchain_zenrows.zenrows_universal_scraper import (
    ZenRowsUniversalScraper,
    ZenRowsUniversalScraperAPIWrapper,
    ZenRowsUniversalScraperInput,
)

__version__ = "0.1.0"

__all__ = [
    "ZenRowsUniversalScraper",
    "ZenRowsUniversalScraperAPIWrapper",
    "ZenRowsUniversalScraperInput",
]
