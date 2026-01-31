# Tools Reference

## list_memory_usage

Get system memory summary (similar to `free -h`).

**Parameters:** None

**Returns:**

| Field | Description |
|-------|-------------|
| `total_gb` | Total physical memory |
| `used_gb` | Used memory |
| `available_gb` | Available memory |
| `percent_used` | Usage percentage |
| `swap_total_gb` | Total swap space |
| `swap_used_gb` | Used swap |

**Example prompt:** "How much memory is available?"

---

## list_top_processes

List processes consuming the most resources.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n` | int | 10 | Number of processes to return |
| `sort_by` | string | "memory" | Sort by "memory" or "cpu" |

**Returns:** List of processes with:

- `pid` - Process ID
- `name` - Process name
- `memory_mb` - Memory usage in MB
- `cpu_percent` - CPU usage percentage
- `username` - Owner

**Example prompt:** "What are the top 5 processes by CPU usage?"

---

## find_stale_processes

Find processes that may be stale based on age or idle time.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_age_hours` | float | None | Minimum process age in hours |
| `min_idle_hours` | float | None | Minimum idle time in hours |
| `name_pattern` | string | None | Filter by name (regex) |

**Returns:** List of matching processes with age and idle information.

**Example prompts:**

- "Find processes running for more than 24 hours"
- "Find idle Chrome processes"

---

## kill_processes

Terminate processes by PID.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pids` | list[int] | required | Process IDs to kill |
| `signal` | string | "SIGTERM" | Signal: "SIGTERM" or "SIGKILL" |
| `confirm_names` | list[string] | None | Expected names (safety check) |

**Returns:** Result for each PID (killed, not found, refused, etc.)

## Safety Mechanisms

The `kill_processes` tool includes several safety features:

!!! warning "Protected PIDs"
    PIDs 0 and 1 are always refused to prevent system damage.

!!! warning "Root Process Protection"
    Processes owned by root are refused unless the server runs as root.

!!! tip "Name Confirmation"
    Use `confirm_names` to verify process names before killing:

    ```
    Kill PID 12345, confirm it's "python"
    ```

    If the name doesn't match, the operation is aborted.

!!! note "Signal Choice"
    - `SIGTERM` (default) - Graceful termination, process can clean up
    - `SIGKILL` - Immediate termination, use only when necessary
