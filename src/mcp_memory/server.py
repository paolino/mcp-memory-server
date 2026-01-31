"""FastMCP server for memory management."""

from fastmcp import FastMCP

from mcp_memory.models import KillSummary, MemoryInfo, ProcessGroup, ProcessInfo
from mcp_memory.tools.kill import kill_processes as _kill_processes
from mcp_memory.tools.memory import list_memory_usage as _list_memory_usage
from mcp_memory.tools.processes import (
    find_stale_processes as _find_stale_processes,
    list_process_groups as _list_process_groups,
    list_top_processes as _list_top_processes,
)

mcp = FastMCP(
    name="mcp-memory",
    instructions="""Memory management server for inspecting system memory and processes.

Available tools:
- list_memory_usage: Get system memory summary (like `free -h`)
- list_top_processes: Find top memory/CPU consumers
- list_process_groups: Aggregate processes by name with totals
- find_stale_processes: Find old/idle processes by criteria
- kill_processes: Terminate processes with safety checks
""",
)


@mcp.tool()
def list_memory_usage() -> MemoryInfo:
    """
    Get system memory usage summary.

    Returns total, available, used memory and swap statistics,
    similar to the `free -h` command.
    """
    return _list_memory_usage()


@mcp.tool()
def list_top_processes(
    n: int = 10,
    sort_by: str = "memory",
) -> list[ProcessInfo]:
    """
    List top N memory-consuming processes.

    Args:
        n: Number of processes to return (default 10, max 100)
        sort_by: Sort criterion - "memory" (default) or "cpu"

    Returns:
        List of processes sorted by the specified criterion
    """
    return _list_top_processes(n=n, sort_by=sort_by)


@mcp.tool()
def list_process_groups(
    n: int = 10,
    min_count: int = 1,
) -> list[ProcessGroup]:
    """
    List processes grouped by name with aggregated stats.

    Useful for seeing total resource usage by process type
    (e.g., "3 claude processes using 1.6GB total").

    Args:
        n: Number of groups to return (default 10, max 50)
        min_count: Minimum number of instances to include (default 1)

    Returns:
        List of process groups sorted by total memory usage descending
    """
    return _list_process_groups(n=n, min_count=min_count)


@mcp.tool()
def find_stale_processes(
    min_age_hours: float = 1.0,
    states: list[str] | None = None,
    name_pattern: str | None = None,
    min_memory_mb: float = 0,
) -> list[ProcessInfo]:
    """
    Find potentially stale processes based on various criteria.

    Useful for finding long-running background processes that may be
    consuming resources unnecessarily.

    Args:
        min_age_hours: Minimum process age in hours (default 1.0)
        states: Process states to include (default ["sleeping"]).
                Valid: sleeping, zombie, stopped, idle, running, disk-sleep
        name_pattern: Regex pattern to match process names (e.g., "ghc|cabal")
        min_memory_mb: Minimum memory usage in MB (default 0)

    Returns:
        List of matching processes, sorted by memory usage descending
    """
    return _find_stale_processes(
        min_age_hours=min_age_hours,
        states=states,
        name_pattern=name_pattern,
        min_memory_mb=min_memory_mb,
    )


@mcp.tool()
def kill_processes(
    pids: list[int],
    signal_name: str = "SIGTERM",
    confirm_names: dict[int, str] | None = None,
) -> KillSummary:
    """
    Kill processes by PID with safety checks.

    Safety mechanisms:
    - Refuses to kill PID 0 or 1
    - Refuses root-owned processes unless running as root
    - Optional name confirmation to prevent killing wrong process
    - Uses SIGTERM by default, SIGKILL only when explicit

    Args:
        pids: List of process IDs to kill
        signal_name: Signal to send - "SIGTERM" (default) or "SIGKILL"
        confirm_names: Optional dict mapping PID to expected process name.
                       Aborts kill for a PID if its name doesn't match.

    Returns:
        Summary with per-PID results including success/failure reasons
    """
    return _kill_processes(
        pids=pids,
        signal_name=signal_name,
        confirm_names=confirm_names,
    )
