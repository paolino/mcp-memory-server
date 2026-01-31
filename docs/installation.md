# Installation

## With Nix (recommended)

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "mcp-memory": {
      "command": "nix",
      "args": ["run", "github:paolino/mcp-memory-server"]
    }
  }
}
```

## With pip

```bash
pip install mcp-memory-server
```

Then configure:

```json
{
  "mcpServers": {
    "mcp-memory": {
      "command": "python",
      "args": ["-m", "mcp_memory"]
    }
  }
}
```

## With uvx

```json
{
  "mcpServers": {
    "mcp-memory": {
      "command": "uvx",
      "args": ["mcp-memory-server"]
    }
  }
}
```

## Verify Installation

After configuring, ask Claude: "How much memory is available on this system?"

You should see a response with total, used, available memory and swap information.
