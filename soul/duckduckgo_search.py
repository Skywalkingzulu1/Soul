"""DuckDuckGo search integration for Andile.

This module provides search functionality using DuckDuckGo's HTML interface.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

try:
    from ddgs import DDGS

    DDGS_AVAILABLE = True
except ImportError:
    try:
        from ddgs import DDGS

        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False
        logger.warning(
            "ddgs package not available. Install with: pip install duckduckgo-search"
        )


def search(query: str, top_n: int = 5, recency_days: int = 365) -> str:
    """Search DuckDuckGo and return formatted results.

    Args:
        query: Search query string
        top_n: Number of results to return (default 5)
        recency_days: Filter results from last N days (default 365)

    Returns:
        Formatted string of search results
    """
    if not DDGS_AVAILABLE:
        return "Search not available. Install duckduckgo-search package."

    try:
        results = []

        # Determine time constraint
        time_map = {
            1: "d",  # Past 24 hours
            7: "w",  # Past week
            30: "m",  # Past month
            365: "y",  # Past year
        }
        time_constraint = "y"  # Default to year
        for days, code in time_map.items():
            if recency_days <= days:
                time_constraint = code
                break

        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=top_n):
                title = r.get("title", "No title")
                href = r.get("href", "")
                body = r.get("body", "")

                results.append(f"**{title}**\n{body}\n{href}")

        if not results:
            return f"No results found for: {query}"

        return "\n\n".join(results)

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search failed: {str(e)}"


def chat_search(query: str, context: str = "") -> str:
    """Search with conversational context.

    Args:
        query: The search query
        context: Additional context for the search

    Returns:
        Search results with context applied
    """
    full_query = f"{context} {query}" if context else query
    return search(full_query, top_n=3)


def quick_search(query: str) -> str:
    """Quick single-result search.

    Args:
        query: Search query

    Returns:
        First search result as string
    """
    results = search(query, top_n=1)
    # Return just the first result
    if results and "\n\n" in results:
        return results.split("\n\n")[0]
    return results


def search_news(query: str, limit: int = 5) -> str:
    """Search for news articles.

    Args:
        query: Search query
        limit: Number of results

    Returns:
        News search results
    """
    if not DDGS_AVAILABLE:
        return "Search not available. Install duckduckgo-search package."

    try:
        results = []

        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=limit):
                title = r.get("title", "No title")
                date = r.get("date", "")
                body = r.get("body", "")
                url = r.get("url", "")

                date_str = f"[{date}] " if date else ""
                results.append(f"{date_str}**{title}**\n{body}\n{url}")

        if not results:
            return f"No news results for: {query}"

        return "\n\n".join(results)

    except Exception as e:
        logger.error(f"News search failed: {e}")
        return f"News search failed: {str(e)}"
