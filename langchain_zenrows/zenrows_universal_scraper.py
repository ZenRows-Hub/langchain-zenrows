"""Deprecated — use `langchain_zenrows.zenrows_fetch` instead.

Kept only for backward compatibility: `ZenRowsUniversalScraper` (and its
input schema / legacy wrapper alias) still work exactly as before, but are
now thin, deprecated redirects onto the current `ZenrowsFetch` tool.
"""

import warnings

from langchain_zenrows.zenrows_fetch import ZenrowsFetch, ZenrowsFetchInput

# Deprecated alias. The input schema carries no identity of its own (no
# registered "name" the way a tool has), so a plain alias is enough - no
# behavior difference from ZenrowsFetchInput.
ZenRowsUniversalScraperInput = ZenrowsFetchInput


class ZenRowsUniversalScraper(ZenrowsFetch):
    """Deprecated: use `ZenrowsFetch` instead.

    A thin, deprecated redirect onto `ZenrowsFetch` - behavior, tool
    ``name`` ("zenrows_fetch"), and ``args_schema`` are identical. This
    class exists only so existing imports keep working while callers
    migrate. New code should use `ZenrowsFetch` directly.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "ZenRowsUniversalScraper is deprecated and will be removed in a "
            "future release; use ZenrowsFetch instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


# For backward compatibility and easier imports
ZenRowsUniversalScraperAPIWrapper = ZenRowsUniversalScraper
