"""Process termination with safety checks."""

import os
import signal

import psutil

from mcp_memory.models import KillResult, KillSummary

# Protected PIDs that should never be killed
PROTECTED_PIDS = {0, 1}


def _is_running_as_root() -> bool:
    """Check if current process is running as root."""
    return os.geteuid() == 0


def _check_safety(pid: int, confirm_name: str | None = None) -> tuple[bool, str, str | None]:
    """
    Check if it's safe to kill a process.

    Returns:
        Tuple of (is_safe, message, process_name)
    """
    if pid in PROTECTED_PIDS:
        return False, f"PID {pid} is protected (init/kernel)", None

    try:
        proc = psutil.Process(pid)
        name = proc.name()
        username = proc.username()
    except psutil.NoSuchProcess:
        return False, f"PID {pid} does not exist", None
    except psutil.AccessDenied:
        return False, f"Access denied to PID {pid}", None

    # Refuse root-owned processes unless running as root
    if username == "root" and not _is_running_as_root():
        return False, f"PID {pid} ({name}) is owned by root", name

    # Check name confirmation if requested
    if confirm_name is not None and name != confirm_name:
        return (
            False,
            f"PID {pid} name mismatch: expected '{confirm_name}', got '{name}'",
            name,
        )

    return True, "OK", name


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
                       If provided, abort kill if name doesn't match.

    Returns:
        KillSummary with per-PID results
    """
    if confirm_names is None:
        confirm_names = {}

    # Validate signal
    sig = signal.SIGTERM
    if signal_name.upper() == "SIGKILL":
        sig = signal.SIGKILL
    elif signal_name.upper() != "SIGTERM":
        return KillSummary(
            requested=len(pids),
            succeeded=0,
            failed=0,
            refused=len(pids),
            results=[
                KillResult(
                    pid=pid,
                    success=False,
                    message=f"Invalid signal: {signal_name}. Use SIGTERM or SIGKILL.",
                )
                for pid in pids
            ],
        )

    results: list[KillResult] = []
    succeeded = 0
    failed = 0
    refused = 0

    for pid in pids:
        confirm_name = confirm_names.get(pid)
        is_safe, message, name = _check_safety(pid, confirm_name)

        if not is_safe:
            refused += 1
            results.append(
                KillResult(
                    pid=pid,
                    success=False,
                    message=f"Refused: {message}",
                    name=name,
                )
            )
            continue

        # Attempt to kill
        try:
            os.kill(pid, sig)
            succeeded += 1
            results.append(
                KillResult(
                    pid=pid,
                    success=True,
                    message=f"Sent {signal_name} to {name}",
                    name=name,
                )
            )
        except ProcessLookupError:
            failed += 1
            results.append(
                KillResult(
                    pid=pid,
                    success=False,
                    message="Process no longer exists",
                    name=name,
                )
            )
        except PermissionError:
            failed += 1
            results.append(
                KillResult(
                    pid=pid,
                    success=False,
                    message="Permission denied",
                    name=name,
                )
            )
        except OSError as e:
            failed += 1
            results.append(
                KillResult(
                    pid=pid,
                    success=False,
                    message=f"OS error: {e}",
                    name=name,
                )
            )

    return KillSummary(
        requested=len(pids),
        succeeded=succeeded,
        failed=failed,
        refused=refused,
        results=results,
    )
