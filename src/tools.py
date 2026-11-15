import asyncio
import os
from mcp import Client

# Where Joshua's MCP server is
URL = os.getenv("MCP_URL", "http://localhost:8000/mcp")


# The MCP library only works with "async" code,
# so this function makes one call and waits for the answer
async def call_async(name, args):
    async with Client(URL) as client:
        res = await client.call_tool(name, args)
    if res.is_error:
        return None
    return res.structured_content


# Call one of Joshua's tools, like call_tool("summarize_category", {"category": "'es_food'"})
def call_tool(name, args):
    return asyncio.run(call_async(name, args))
