"""Memory usage tool."""

import psutil

from mcp_memory.models import MemoryInfo

# Warning thresholds
MEMORY_WARNING_PERCENT = 80
MEMORY_CRITICAL_PERCENT = 95
SWAP_WARNING_PERCENT = 50


def _generate_warnings(mem_percent: float, swap_percent: float) -> list[str]:
    """Generate health warnings based on memory usage."""
    warnings = []

    if mem_percent >= MEMORY_CRITICAL_PERCENT:
        warnings.append(f"CRITICAL: Memory usage at {mem_percent}%")
    elif mem_percent >= MEMORY_WARNING_PERCENT:
        warnings.append(f"High memory usage: {mem_percent}%")

    if swap_percent >= SWAP_WARNING_PERCENT:
        warnings.append(f"High swap usage: {swap_percent}%")

    return warnings


def list_memory_usage() -> MemoryInfo:
    """
    Get system memory usage summary.

    Returns information similar to `free -h`: total, available, used memory
    and swap statistics. Includes warnings for high resource usage.
    """
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    mem_percent = round(mem.percent, 1)
    swap_percent = round(swap.percent, 1)

    return MemoryInfo(
        total_gb=round(mem.total / (1024**3), 2),
        available_gb=round(mem.available / (1024**3), 2),
        used_gb=round(mem.used / (1024**3), 2),
        used_percent=mem_percent,
        swap_total_gb=round(swap.total / (1024**3), 2),
        swap_used_gb=round(swap.used / (1024**3), 2),
        swap_percent=swap_percent,
        warnings=_generate_warnings(mem_percent, swap_percent),
    )
