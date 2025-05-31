# MCP Web Search Crawler

A Model Context Protocol (MCP) server that provides web search and crawling capabilities. This server enables AI assistants and other MCP clients to search the web using DuckDuckGo and crawl specific URLs to extract content in markdown format.

## Features

- **Web Search**: Search the web using DuckDuckGo and return link titles
- **URL Crawling**: Crawl specific URLs and return their content as markdown
- **MCP Integration**: Seamlessly integrates with any MCP-compatible client
- **Fast and Efficient**: Built with modern Python tools including UV and FastMCP

## Installation

First clone the repository locally:
```bash
git clone https://github.com/tomas-hanzlik/mcp-web-search-crawl
cd mcp-web-search-crawl
```

## Configuration

Configure the server in your MCP client:

```json
{
    "mcpServers": {
        "mcp-web-search-crawl": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/src/mcp_web_search_crawl",
                "run",
                "mcpsearchcrawl"
            ]
        }
    }
}
```

Alternatively, you can also configure using the following command:
```bash
uvx --from git+https://github.com/tomas-hanzlik/mcp-web-search-crawl mcpsearchcrawl
```

## Testing Configurations Programmatically

Test the server programmatically using a Python client:

```python
from fastmcp import Client

config = {
    "mcpServers": {
        "mcp-web-search-crawl": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/src/mcp_web_search_crawl",
                "run",
                "mcpsearchcrawl"
            ]
        }
    }
}

# Create a client that connects to all servers
client = Client(config)

async def main():
    async with client:
        # Access tools and resources with server prefixes
        answer = await client.call_tool("search_links", {"query": "What is MCP?"})
        print("Search Links Result:", answer)
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Development Setup

Set up the development environment:

```bash
uv venv
uv run mcpsearchcrawl --transport sse # or stdio as alternative
```

## Debugging with MCP Inspector

Debug the server using MCP Inspector:

```bash
uv run fastmcp dev src/mcp_web_search_crawl/server.py:mcp --with-editable .
```

<!-- 
Azure Container App registry push
export ACR_NAME=myregistryname

az login
az acr login --name $ACR_NAME

docker build --tag $ACR_NAME.azurecr.io/mcp-web-search-crawl .  --platform linux/amd64

docker push $ACR_NAME.azurecr.io/mcp-web-search-crawl
 -->