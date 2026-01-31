# MCP Memory Server

[![CI](https://github.com/paolino/mcp-memory-server/actions/workflows/CI.yaml/badge.svg)](https://github.com/paolino/mcp-memory-server/actions/workflows/CI.yaml)

MCP server for memory management with process inspection and cleanup tools.

**[Documentation](https://paolino.github.io/mcp-memory-server/)**

## Tools

| Tool | Description |
|------|-------------|
| `list_memory_usage` | System memory summary (like `free -h`) |
| `list_top_processes` | Top N memory consumers with details |
| `find_stale_processes` | Find sleeping/idle processes by age, state, name pattern |
| `kill_processes` | Kill PIDs with safety checks |

## Installation

### Claude Code

Add to `~/.config/claude-code/mcp.json`:

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

### From source

```bash
git clone https://github.com/paolino/mcp-memory-server
cd mcp-memory-server
nix develop
just install
just run
```

## Usage Examples

### Show memory usage

Ask Claude: "Show me current memory usage"

### Find stale GHC processes

Ask Claude: "Find old GHC or cabal processes using more than 100MB"

This calls `find_stale_processes` with:
- `name_pattern`: `"ghc|cabal"`
- `min_memory_mb`: `100`

### Kill processes

Ask Claude: "Kill these PIDs: 1234, 5678"

Safety checks:
- Refuses PID 0/1
- Refuses root-owned processes (unless running as root)
- Optional name confirmation to prevent killing wrong process
- Default SIGTERM, SIGKILL only when explicit

## Development

```bash
nix develop
just test       # Run tests
just run        # Start server
just format     # Format code
just lint       # Lint code
```

## License

MIT
