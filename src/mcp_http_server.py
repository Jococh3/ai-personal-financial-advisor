"""I expose my E516 financial tools through Streamable HTTP."""

import os
import uvicorn

from mcp_server import mcp

HOST = os.getenv("E516_MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("E516_MCP_PORT", "8000"))

app = mcp.streamable_http_app(
    host=HOST,
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )
