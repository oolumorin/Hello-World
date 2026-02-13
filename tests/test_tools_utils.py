"""Tests for utility tools (datetime, decision logging)."""

import os
from datetime import datetime

import pytest

from executive_coach.tools.utils import (
    get_current_datetime,
    log_decision,
    get_decision_log,
)


@pytest.fixture(autouse=True)
def vault_dir(tmp_path, monkeypatch):
    """Create a temporary vault directory and set the env var."""
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))
    return tmp_path


def test_get_current_datetime():
    result = get_current_datetime()
    assert "date" in result
    assert "time" in result
    assert "day_of_week" in result
    assert "iso_week" in result
    # Date format should be YYYY-MM-DD
    datetime.strptime(result["date"], "%Y-%m-%d")


def test_log_decision(vault_dir):
    result = log_decision(
        title="Adopt new framework",
        context="We need a frontend framework for the new project.",
        options="React, Vue, Svelte",
        analysis="React has the largest ecosystem; Vue is simpler.",
        decision="React",
        rationale="Team familiarity and ecosystem support.",
        expected_outcome="Faster development velocity within 2 sprints.",
        review_date="2026-04-01",
    )
    assert result["status"] == "logged"
    assert "coach/decisions/" in result["path"]

    # Verify the file was created
    full_path = vault_dir / result["path"]
    assert full_path.exists()
    content = full_path.read_text()
    assert "Adopt new framework" in content
    assert "pending-review" in content
    assert "2026-04-01" in content


def test_get_decision_log_empty(vault_dir):
    result = get_decision_log()
    assert result["decisions"] == []
    assert result["count"] == 0


def test_get_decision_log_with_entries(vault_dir):
    # Log two decisions
    log_decision(
        title="Decision A",
        context="ctx",
        options="opt",
        analysis="analysis",
        decision="A",
        rationale="reason",
        expected_outcome="outcome",
        review_date="2026-03-01",
    )
    log_decision(
        title="Decision B",
        context="ctx",
        options="opt",
        analysis="analysis",
        decision="B",
        rationale="reason",
        expected_outcome="outcome",
        review_date="2026-06-01",
    )

    result = get_decision_log()
    assert result["count"] == 2


def test_get_decision_log_with_filter(vault_dir):
    log_decision(
        title="Filtered Decision",
        context="ctx",
        options="opt",
        analysis="analysis",
        decision="X",
        rationale="reason",
        expected_outcome="outcome",
        review_date="2026-03-01",
    )

    # All decisions are logged with status "pending-review"
    result = get_decision_log(status_filter="pending-review")
    assert result["count"] >= 1

    result = get_decision_log(status_filter="reviewed")
    assert result["count"] == 0
