"""Optional MCP provider for financial calculations.

Install `mcp` using requirements-integration.txt on the host serving tools.
Run from project root: python src/mcp_server.py
The stdio transport is intended for a locally launched MCP client. For
remote/cloud deployment, coordinate HTTP transport and auth with Matthew.
"""
from financial_tools import get_customer_spending, summarize_category

try:
    from mcp.server.mcpserver import MCPServer
except ImportError as exc:
    raise SystemExit("Install optional MCP dependency: pip install -r requirements-integration.txt") from exc

mcp = MCPServer("e516-financial-tools")
mcp.tool()(get_customer_spending)
mcp.tool()(summarize_category)

if __name__ == "__main__":
    mcp.run()
