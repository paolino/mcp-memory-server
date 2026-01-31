"""Process inspection tools."""

import re
import time
from datetime import datetime

import psutil

from mcp_memory.models import ProcessGroup, ProcessInfo


def _format_age(hours: float) -> str:
    """Format age in hours to human-readable string."""
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes}m"
    elif hours < 24:
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h}h {m}m" if m > 0 else f"{h}h"
    else:
        days = int(hours / 24)
        remaining_hours = int(hours % 24)
        return f"{days}d {remaining_hours}h" if remaining_hours > 0 else f"{days}d"


def _format_timestamp(ts: float) -> str:
    """Format Unix timestamp to human-readable string."""
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%b %d %H:%M")


def _get_process_info(proc: psutil.Process) -> ProcessInfo | None:
    """Extract process info, returning None if process disappears."""
    try:
        with proc.oneshot():
            create_time = proc.create_time()
            age_hours = (time.time() - create_time) / 3600
            cmdline = proc.cmdline()
            cmdline_str = " ".join(cmdline)[:200] if cmdline else ""

            return ProcessInfo(
                pid=proc.pid,
                name=proc.name(),
                username=proc.username(),
                memory_mb=round(proc.memory_info().rss / (1024**2), 2),
                memory_percent=round(proc.memory_percent(), 2),
                cpu_percent=round(proc.cpu_percent(interval=0.0), 1),
                status=proc.status(),
                create_time=create_time,
                age_hours=round(age_hours, 2),
                age_formatted=_format_age(age_hours),
                started_at=_format_timestamp(create_time),
                cmdline=cmdline_str,
            )
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None


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
        List of ProcessInfo sorted by the specified criterion
    """
    n = min(max(1, n), 100)

    processes: list[ProcessInfo] = []
    for proc in psutil.process_iter():
        info = _get_process_info(proc)
        if info is not None:
            processes.append(info)

    if sort_by == "cpu":
        processes.sort(key=lambda p: p.cpu_percent, reverse=True)
    else:
        processes.sort(key=lambda p: p.memory_mb, reverse=True)

    return processes[:n]


def find_stale_processes(
    min_age_hours: float = 1.0,
    states: list[str] | None = None,
    name_pattern: str | None = None,
    min_memory_mb: float = 0,
) -> list[ProcessInfo]:
    """
    Find potentially stale processes based on various criteria.

    Args:
        min_age_hours: Minimum process age in hours (default 1.0)
        states: Process states to include (default ["sleeping"]).
                Valid states: sleeping, zombie, stopped, idle, running, disk-sleep
        name_pattern: Regex pattern to match process names (e.g., "ghc|cabal")
        min_memory_mb: Minimum memory usage in MB (default 0)

    Returns:
        List of ProcessInfo matching the criteria, sorted by memory usage
    """
    if states is None:
        states = ["sleeping"]

    # Normalize state names
    state_set = {s.lower() for s in states}

    # Compile regex if provided
    pattern = re.compile(name_pattern, re.IGNORECASE) if name_pattern else None

    matches: list[ProcessInfo] = []
    for proc in psutil.process_iter():
        info = _get_process_info(proc)
        if info is None:
            continue

        # Check age
        if info.age_hours < min_age_hours:
            continue

        # Check state
        if info.status.lower() not in state_set:
            continue

        # Check memory
        if info.memory_mb < min_memory_mb:
            continue

        # Check name pattern
        if pattern and not pattern.search(info.name):
            continue

        matches.append(info)

    # Sort by memory usage descending
    matches.sort(key=lambda p: p.memory_mb, reverse=True)
    return matches


def list_process_groups(
    n: int = 10,
    min_count: int = 1,
) -> list[ProcessGroup]:
    """
    List processes grouped by name with aggregated stats.

    Args:
        n: Number of groups to return (default 10, max 50)
        min_count: Minimum number of instances to include (default 1)

    Returns:
        List of ProcessGroup sorted by total memory usage descending
    """
    n = min(max(1, n), 50)
    min_count = max(1, min_count)

    groups: dict[str, dict] = {}
    for proc in psutil.process_iter():
        info = _get_process_info(proc)
        if info is None:
            continue

        name = info.name
        if name not in groups:
            groups[name] = {
                "pids": [],
                "total_memory_mb": 0.0,
                "total_memory_percent": 0.0,
            }
        groups[name]["pids"].append(info.pid)
        groups[name]["total_memory_mb"] += info.memory_mb
        groups[name]["total_memory_percent"] += info.memory_percent

    result = [
        ProcessGroup(
            name=name,
            count=len(data["pids"]),
            total_memory_mb=round(data["total_memory_mb"], 2),
            total_memory_percent=round(data["total_memory_percent"], 2),
            pids=data["pids"],
        )
        for name, data in groups.items()
        if len(data["pids"]) >= min_count
    ]

    result.sort(key=lambda g: g.total_memory_mb, reverse=True)
    return result[:n]
