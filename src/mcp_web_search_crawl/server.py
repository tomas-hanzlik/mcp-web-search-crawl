from cachetools import TTLCache
from fastmcp import Context, FastMCP
from loguru import logger
from pydantic import BaseModel

from mcp_web_search_crawl.config import settings
from mcp_web_search_crawl.utils import crawl_pages, search_web

# TTL cache for storing search results and crawled content to improve performance
CACHE = TTLCache(maxsize=settings.cache_max_size, ttl=settings.cache_ttl_seconds)

mcp = FastMCP("Web Search & Crawler 🚀", host=settings.host, port=settings.port)


class SearchResult(BaseModel):
    url: str
    title: str
    body_snippet: str | None = None


class CrawledContent(BaseModel):
    url: str
    markdown: str


@mcp.tool(
    description="Search the web for a given query and return link titles only. Use this tool when the user asks about finding web pages or getting search results without detailed content."
)
async def search_links(query: str, ctx: Context) -> list[SearchResult]:
    """
    Search the web for a given query and return link titles only.

    Use this tool when you need to find web pages related to a topic but don't need
    the full content. Returns search results with URLs, titles, and brief snippets.

    Args:
        query: The search query string to look for on the web.

    Returns:
        A list of SearchResult objects, each containing:
        - url: The URL of the search result
        - title: The title of the web page
        - body_snippet: A snippet of content from the web page (if available)
    """
    try:
        # Check cache first to avoid redundant API calls
        if query in CACHE:
            await ctx.info(f"🔍 Returning cached search results for: '{query}'")
            return CACHE[query]

        await ctx.info(f"🔍 Searching for links: '{query}'")

        search_results = await search_web(query)

        # Cache results to improve performance for repeated queries
        CACHE[query] = search_results

        await ctx.info(f"✅ Found {len(search_results)} search results")
        return [
            SearchResult(
                url=result["href"],
                title=result["title"],
                body_snippet=result.get("body", None),
            )
            for result in search_results
        ]

    except Exception as e:
        error_msg = f"Link search failed: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        return {"error": error_msg}


@mcp.tool(
    description="Crawl specific URLs and return their content as markdown. Use this tool when you need the full content from specific web pages for analysis or summarization."
)
async def crawl_urls(urls: list[str], ctx: Context) -> list[CrawledContent]:
    """
    Crawl specific URLs and return their content as markdown.

    Use this tool when you need to extract and analyze the full content from
    specific web pages. Takes URLs and returns their content in markdown format.

    Args:
        urls: List of URLs to crawl and extract content from

    Returns:
        List of CrawledContent objects, each containing the URL and its markdown content.
    """
    try:
        if not urls:
            error_msg = "No valid URLs provided"
            await ctx.error(error_msg)
            return {"error": error_msg}

        # Use a frozenset of sorted URLs as cache key for consistency across calls
        cache_key = frozenset(sorted(urls))
        if cache_key in CACHE:
            await ctx.info(
                f"🕷️ Returning cached crawled content for {len(urls)} URLs..."
            )
            return CACHE[cache_key]

        await ctx.info(f"🕷️ Crawling {len(urls)} URLs...")

        # Crawl the pages and extract their content
        crawled_content = await crawl_pages(urls)

        # Cache the results to avoid re-crawling the same URLs
        CACHE[cache_key] = crawled_content

        await ctx.info(f"✅ Completed crawling {len(crawled_content)} pages")

        return [
            CrawledContent(url=url, markdown=markdown)
            for url, markdown in crawled_content.items()
        ]

    except Exception as e:
        error_msg = f"URL crawling failed: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        return {"error": error_msg}
