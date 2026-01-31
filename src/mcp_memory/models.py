"""Pydantic response models for memory management tools."""

from pydantic import BaseModel, Field


class MemoryInfo(BaseModel):
    """System memory information."""

    total_gb: float = Field(description="Total physical memory in GB")
    available_gb: float = Field(description="Available memory in GB")
    used_gb: float = Field(description="Used memory in GB")
    used_percent: float = Field(description="Memory usage percentage")
    swap_total_gb: float = Field(description="Total swap in GB")
    swap_used_gb: float = Field(description="Used swap in GB")
    swap_percent: float = Field(description="Swap usage percentage")
    warnings: list[str] = Field(
        default_factory=list,
        description="Health warnings (high memory, swap usage, etc.)",
    )


class ProcessInfo(BaseModel):
    """Information about a single process."""

    pid: int = Field(description="Process ID")
    name: str = Field(description="Process name")
    username: str = Field(description="Owner username")
    memory_mb: float = Field(description="Resident memory in MB")
    memory_percent: float = Field(description="Memory usage percentage")
    cpu_percent: float = Field(description="CPU usage percentage")
    status: str = Field(description="Process status")
    create_time: float = Field(description="Process creation time (Unix timestamp)")
    age_hours: float = Field(description="Process age in hours")
    age_formatted: str = Field(description="Human-readable age (e.g., '2h 30m')")
    started_at: str = Field(description="Human-readable start time (e.g., 'Jan 30 14:23')")
    cmdline: str = Field(description="Command line (truncated)")


class ProcessGroup(BaseModel):
    """Aggregated information for processes with the same name."""

    name: str = Field(description="Process name")
    count: int = Field(description="Number of instances")
    total_memory_mb: float = Field(description="Total memory usage in MB")
    total_memory_percent: float = Field(description="Total memory usage percentage")
    pids: list[int] = Field(description="List of process IDs")


class KillResult(BaseModel):
    """Result of attempting to kill a single process."""

    pid: int = Field(description="Process ID")
    success: bool = Field(description="Whether the kill succeeded")
    message: str = Field(description="Status message or error description")
    name: str | None = Field(default=None, description="Process name if available")


class KillSummary(BaseModel):
    """Summary of kill operation results."""

    requested: int = Field(description="Number of PIDs requested to kill")
    succeeded: int = Field(description="Number successfully killed")
    failed: int = Field(description="Number that failed")
    refused: int = Field(description="Number refused due to safety checks")
    results: list[KillResult] = Field(description="Per-PID results")
