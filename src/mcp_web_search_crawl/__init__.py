from mcp_web_search_crawl.server import mcp
from mcp_web_search_crawl.config import settings, TransportMethod
from loguru import logger

from importlib import metadata

try:
    __version__ = metadata.version("mcp-web-search-crawl")
except metadata.PackageNotFoundError:
    __version__ = "unknown"


def start_server() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="MCP Server to search and crawl the web",
    )

    parser.add_argument(
        "-t",
        "--transport",
        type=TransportMethod,
        help="MCP Server Transport: stdio or sse",
        default=settings.transport,
    )

    args = parser.parse_args()

    logger.info(
        f'Starting MCP Teams Server "{__version__}" with transport "{args.transport}"'
    )
    mcp.run(transport=args.transport)


__all__ = [
    "start_server",
]
