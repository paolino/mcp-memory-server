# MCP Memory Server

A Model Context Protocol (MCP) server for system memory monitoring and process management.

## Features

- **Memory monitoring** - Get system memory usage summary
- **Process inspection** - Find top consumers by memory or CPU
- **Stale process detection** - Identify old or idle processes
- **Safe process termination** - Kill processes with built-in safety checks

## Quick Start

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

Then ask Claude:

- "How much memory is available?"
- "What processes are using the most memory?"
- "Find processes running for more than 7 days"
- "Kill process 12345"
