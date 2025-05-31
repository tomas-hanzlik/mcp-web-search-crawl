from loguru import logger
from fastmcp import FastMCP, Context
from cachetools import TTLCache

from mcp_web_search_crawl.config import settings
from mcp_web_search_crawl.utils import search_web, crawl_pages

# TTL cache for storing search results and crawled content to improve performance
CACHE = TTLCache(maxsize=settings.cache_max_size, ttl=settings.cache_ttl_seconds)

mcp = FastMCP("Web Search & Crawler 🚀", host="0.0.0.0", port="8000")


@mcp.tool(
    description="Search the web using DuckDuckGo and get a list of relevant URLs with their titles and a snippet of their content. Use this when you need to find web pages related to a specific topic or query. Returns a list of dictionaries, each containing a URL, its title, and a snippet of content."
)
async def search_links(query: str, ctx: Context) -> list[dict[str, str]]:
    """
    Search the web for a given query and return a list of URLs with their titles and snippets of content.

    This tool uses DuckDuckGo to perform a web search and retrieves the top results
    without crawling the actual page content. It is ideal for discovering relevant
    links, their titles, and a snippet of their content when researching a specific topic or query.

    Use cases:
        - Finding articles or resources related to a specific topic
        - Exploring web pages about a technology, concept, or idea
        - Quickly identifying relevant URLs for further analysis

    Args:
        query: The search query string to look for on the web.

    Returns:
        list[dict[str, str]]: A list of dictionaries, each containing a URL, its corresponding page title, and a snippet of content.
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
        return search_results

    except Exception as e:
        error_msg = f"Link search failed: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        return {"error": error_msg}


@mcp.tool(
    description="Crawl and extract the full content from specific web pages as markdown. Use this when you have URLs and need to read their actual content. Takes a list of URLs and returns their content in markdown format for easy processing and analysis."
)
async def crawl_urls(urls: list[str], ctx: Context) -> dict[str, str]:
    """
    Crawl specific URLs and return their content as markdown.

    This tool takes a list of URLs, fetches their content, and converts it
    to markdown format for easy reading and processing. Use this after you
    have identified specific URLs you want to analyze or extract information from.

    Use cases:
        - Reading the full content of articles or blog posts
        - Extracting structured information from web pages
        - Getting detailed content after finding relevant URLs with search_links
        - Analyzing the content of documentation pages or resources

    Args:
        urls: List of URLs to crawl and extract content from

    Returns:
        dict[str, str]: A dictionary mapping URLs to their markdown content
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
        return crawled_content

    except Exception as e:
        error_msg = f"URL crawling failed: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        return {"error": error_msg}
