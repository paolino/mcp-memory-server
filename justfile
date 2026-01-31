# shellcheck shell=bash

set unstable := true

# List available recipes
default:
    @just --list

# Install dependencies in dev mode
install:
    #!/usr/bin/env bash
    set -euo pipefail
    pip install -e ".[dev]"

# Run unit tests
test match="":
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ '{{ match }}' == "" ]]; then
        pytest tests/ -v
    else
        pytest tests/ -v -k "{{ match }}"
    fi

# Run the MCP server
run:
    #!/usr/bin/env bash
    set -euo pipefail
    python -m mcp_memory

# Format code with ruff
format:
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v ruff &> /dev/null; then
        ruff format src tests
        ruff check --fix src tests
    else
        echo "ruff not installed, skipping format"
    fi

# Lint code
lint:
    #!/usr/bin/env bash
    set -euo pipefail
    if command -v ruff &> /dev/null; then
        ruff check src tests
    else
        echo "ruff not installed, skipping lint"
    fi

# Build with nix
build:
    #!/usr/bin/env bash
    set -euo pipefail
    nix build

# Run CI checks
CI:
    #!/usr/bin/env bash
    set -euo pipefail
    just test
    just lint

# Clean build artifacts
clean:
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf dist build *.egg-info result .pytest_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
