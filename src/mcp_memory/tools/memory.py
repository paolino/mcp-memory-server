"""Memory usage tool."""

import psutil

from mcp_memory.models import MemoryInfo


def list_memory_usage() -> MemoryInfo:
    """
    Get system memory usage summary.

    Returns information similar to `free -h`: total, available, used memory
    and swap statistics.
    """
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return MemoryInfo(
        total_gb=round(mem.total / (1024**3), 2),
        available_gb=round(mem.available / (1024**3), 2),
        used_gb=round(mem.used / (1024**3), 2),
        used_percent=round(mem.percent, 1),
        swap_total_gb=round(swap.total / (1024**3), 2),
        swap_used_gb=round(swap.used / (1024**3), 2),
        swap_percent=round(swap.percent, 1),
    )
