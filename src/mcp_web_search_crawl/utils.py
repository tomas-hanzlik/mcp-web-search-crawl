from loguru import logger
from duckduckgo_search import DDGS
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai import BrowserConfig as Crawl4aiBrowserConfig

from .config import settings


async def search_web(query: str) -> list[dict[str, str]]:
    """
    Search the web asynchronously using DuckDuckGo.

    Args:
        query: Search query string

    Returns:
        List of search results, where each result is a dictionary
        of string keys to string values (e.g., 'href', 'title', 'body').

    Raises:
        Exception: If search operation fails
    """
    try:
        logger.info(f"Performing asynchronous web search for query: '{query}'")

        ddgs = DDGS()
        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None, lambda: ddgs.text(query, max_results=settings.max_search_results)
        )

        logger.info(f"Found {len(results)} search results")
        return results

    except Exception as e:
        logger.error(f"Async search failed for query '{query}': {str(e)}")
        raise Exception(f"Async web search failed: {str(e)}")


async def crawl_pages(urls: list[str]) -> dict[str, str]:
    """
    Crawl multiple web pages and extract their content as markdown.

    Args:
        urls: List of URLs to crawl

    Returns:
        Dictionary mapping URLs to their markdown content

    Raises:
        Exception: If crawling operation fails
    """
    try:
        logger.info(f"Starting to crawl {len(urls)} pages")

        browser_config = Crawl4aiBrowserConfig(
            browser_type=settings.browser_config.browser_type,
            headless=settings.browser_config.headless,
            verbose=settings.browser_config.verbose,
            user_agent=settings.browser_config.user_agent,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            results = await crawler.arun_many(urls=urls)

        # Process results and handle any failures
        crawled_content = {}
        successful_crawls = 0

        for result in results:
            if result.success:
                crawled_content[result.url] = result.markdown
                successful_crawls += 1
            else:
                logger.warning(f"Failed to crawl {result.url}: {result.error_message}")
                crawled_content[result.url] = (
                    f"Error: Failed to crawl this page - {result.error_message}"
                )

        logger.info(f"Successfully crawled {successful_crawls}/{len(urls)} pages")
        return crawled_content

    except Exception as e:
        logger.error(f"Crawling operation failed: {str(e)}")
        raise Exception(f"Web crawling failed: {str(e)}")
