"""Tests for memory management tools."""

import os

import pytest

from mcp_memory.models import KillSummary, MemoryInfo, ProcessGroup, ProcessInfo
from mcp_memory.tools.kill import kill_processes
from mcp_memory.tools.memory import _generate_warnings, list_memory_usage
from mcp_memory.tools.processes import (
    find_stale_processes,
    list_process_groups,
    list_top_processes,
)


class TestListMemoryUsage:
    """Tests for list_memory_usage."""

    def test_returns_memory_info(self) -> None:
        result = list_memory_usage()
        assert isinstance(result, MemoryInfo)

    def test_total_is_positive(self) -> None:
        result = list_memory_usage()
        assert result.total_gb > 0

    def test_used_percent_in_range(self) -> None:
        result = list_memory_usage()
        assert 0 <= result.used_percent <= 100

    def test_available_less_than_total(self) -> None:
        result = list_memory_usage()
        assert result.available_gb <= result.total_gb

    def test_has_warnings_field(self) -> None:
        result = list_memory_usage()
        assert isinstance(result.warnings, list)


class TestGenerateWarnings:
    """Tests for warning generation."""

    def test_no_warnings_for_low_usage(self) -> None:
        warnings = _generate_warnings(mem_percent=50.0, swap_percent=10.0)
        assert warnings == []

    def test_warning_for_high_memory(self) -> None:
        warnings = _generate_warnings(mem_percent=85.0, swap_percent=0.0)
        assert len(warnings) == 1
        assert "High memory" in warnings[0]

    def test_critical_for_very_high_memory(self) -> None:
        warnings = _generate_warnings(mem_percent=96.0, swap_percent=0.0)
        assert len(warnings) == 1
        assert "CRITICAL" in warnings[0]

    def test_warning_for_high_swap(self) -> None:
        warnings = _generate_warnings(mem_percent=50.0, swap_percent=60.0)
        assert len(warnings) == 1
        assert "swap" in warnings[0].lower()

    def test_multiple_warnings(self) -> None:
        warnings = _generate_warnings(mem_percent=85.0, swap_percent=60.0)
        assert len(warnings) == 2

    def test_threshold_boundary_memory(self) -> None:
        # Just below threshold - no warning
        warnings = _generate_warnings(mem_percent=79.9, swap_percent=0.0)
        assert warnings == []
        # At threshold - warning
        warnings = _generate_warnings(mem_percent=80.0, swap_percent=0.0)
        assert len(warnings) == 1

    def test_threshold_boundary_swap(self) -> None:
        # Just below threshold - no warning
        warnings = _generate_warnings(mem_percent=0.0, swap_percent=49.9)
        assert warnings == []
        # At threshold - warning
        warnings = _generate_warnings(mem_percent=0.0, swap_percent=50.0)
        assert len(warnings) == 1


class TestListTopProcesses:
    """Tests for list_top_processes."""

    def test_returns_list(self) -> None:
        result = list_top_processes(n=5)
        assert isinstance(result, list)
        assert len(result) <= 5

    def test_respects_limit(self) -> None:
        result = list_top_processes(n=3)
        assert len(result) <= 3

    def test_clamps_max_to_100(self) -> None:
        result = list_top_processes(n=200)
        assert len(result) <= 100

    def test_items_are_process_info(self) -> None:
        result = list_top_processes(n=5)
        for item in result:
            assert isinstance(item, ProcessInfo)

    def test_sorted_by_memory_descending(self) -> None:
        result = list_top_processes(n=10, sort_by="memory")
        for i in range(len(result) - 1):
            assert result[i].memory_mb >= result[i + 1].memory_mb

    def test_sorted_by_cpu_descending(self) -> None:
        result = list_top_processes(n=10, sort_by="cpu")
        for i in range(len(result) - 1):
            assert result[i].cpu_percent >= result[i + 1].cpu_percent


class TestListProcessGroups:
    """Tests for list_process_groups."""

    def test_returns_list(self) -> None:
        result = list_process_groups(n=5)
        assert isinstance(result, list)
        assert len(result) <= 5

    def test_items_are_process_group(self) -> None:
        result = list_process_groups(n=5)
        for item in result:
            assert isinstance(item, ProcessGroup)

    def test_respects_limit(self) -> None:
        result = list_process_groups(n=3)
        assert len(result) <= 3

    def test_clamps_max_to_50(self) -> None:
        result = list_process_groups(n=100)
        assert len(result) <= 50

    def test_sorted_by_memory_descending(self) -> None:
        result = list_process_groups(n=10)
        for i in range(len(result) - 1):
            assert result[i].total_memory_mb >= result[i + 1].total_memory_mb

    def test_min_count_filters(self) -> None:
        result = list_process_groups(n=50, min_count=2)
        for group in result:
            assert group.count >= 2

    def test_pids_match_count(self) -> None:
        result = list_process_groups(n=10)
        for group in result:
            assert len(group.pids) == group.count

    def test_has_required_fields(self) -> None:
        result = list_process_groups(n=1)
        if result:
            group = result[0]
            assert group.name
            assert group.count >= 1
            assert group.total_memory_mb >= 0
            assert group.total_memory_percent >= 0
            assert isinstance(group.pids, list)


class TestFindStaleProcesses:
    """Tests for find_stale_processes."""

    def test_returns_list(self) -> None:
        result = find_stale_processes()
        assert isinstance(result, list)

    def test_respects_min_age(self) -> None:
        result = find_stale_processes(min_age_hours=0.001)  # ~3.6 seconds
        for proc in result:
            assert proc.age_hours >= 0.001

    def test_respects_states_filter(self) -> None:
        result = find_stale_processes(states=["sleeping"], min_age_hours=0)
        for proc in result:
            assert proc.status.lower() == "sleeping"

    def test_respects_min_memory(self) -> None:
        result = find_stale_processes(min_memory_mb=1.0, min_age_hours=0)
        for proc in result:
            assert proc.memory_mb >= 1.0

    def test_name_pattern_filters(self) -> None:
        # Use a pattern that should match at least some processes
        result = find_stale_processes(name_pattern="python", min_age_hours=0)
        for proc in result:
            assert "python" in proc.name.lower()


class TestKillProcesses:
    """Tests for kill_processes."""

    def test_refuses_pid_0(self) -> None:
        result = kill_processes([0])
        assert isinstance(result, KillSummary)
        assert result.refused == 1
        assert result.succeeded == 0
        assert "protected" in result.results[0].message.lower()

    def test_refuses_pid_1(self) -> None:
        result = kill_processes([1])
        assert result.refused == 1
        assert result.succeeded == 0

    def test_refuses_invalid_signal(self) -> None:
        result = kill_processes([12345], signal_name="INVALID")
        assert result.refused == 1
        assert "invalid signal" in result.results[0].message.lower()

    def test_nonexistent_pid_fails(self) -> None:
        # Use a very high PID that's unlikely to exist
        result = kill_processes([999999999])
        # Should either be refused (if safety check fails) or failed (process lookup)
        assert result.succeeded == 0

    def test_returns_summary(self) -> None:
        result = kill_processes([])
        assert isinstance(result, KillSummary)
        assert result.requested == 0
        assert result.succeeded == 0
        assert result.failed == 0
        assert result.refused == 0

    def test_name_confirmation_mismatch(self) -> None:
        # Get our own PID and try to kill with wrong name
        pid = os.getpid()
        result = kill_processes([pid], confirm_names={pid: "definitely_not_python"})
        assert result.refused == 1
        assert "mismatch" in result.results[0].message.lower()

    def test_accepts_sigterm(self) -> None:
        result = kill_processes([999999999], signal_name="SIGTERM")
        # Should not fail due to signal validation
        assert all(
            "invalid signal" not in r.message.lower() for r in result.results
        )

    def test_accepts_sigkill(self) -> None:
        result = kill_processes([999999999], signal_name="SIGKILL")
        # Should not fail due to signal validation
        assert all(
            "invalid signal" not in r.message.lower() for r in result.results
        )
