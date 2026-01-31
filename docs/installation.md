# Installation

## With Nix (recommended)

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "mcp-memory": {
      "command": "nix",
      "args": ["run", "github:paolino/mcp-memory-server", "--refresh"]
    }
  }
}
```

### Updating

The `--refresh` flag ensures Nix fetches the latest version from GitHub on each run. Without it, Nix uses its cached version.

For faster startup (using cached version):

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

To manually update the cache, run:

```bash
nix flake prefetch github:paolino/mcp-memory-server --refresh
```

To pin a specific version:

```json
{
  "mcpServers": {
    "mcp-memory": {
      "command": "nix",
      "args": ["run", "github:paolino/mcp-memory-server/v0.1.0"]
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
