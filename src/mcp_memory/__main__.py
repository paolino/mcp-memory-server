"""Entry point for mcp-memory server."""

from mcp_memory.server import mcp


def main() -> None:
    """Run the MCP memory server."""
    mcp.run()


if __name__ == "__main__":
    main()
