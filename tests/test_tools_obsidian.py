"""Tests for Obsidian vault tools."""

import os
import tempfile
from pathlib import Path

import pytest

from executive_coach.tools.obsidian import (
    read_obsidian_note,
    write_obsidian_note,
    list_obsidian_notes,
    search_obsidian_vault,
)


@pytest.fixture(autouse=True)
def vault_dir(tmp_path, monkeypatch):
    """Create a temporary vault directory and set the env var."""
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))
    # Seed some test notes
    coach_dir = tmp_path / "coach" / "goals"
    coach_dir.mkdir(parents=True)
    (coach_dir / "quarterly-goals.md").write_text(
        "# Q1 OKRs\n\n- [ ] KR1: Ship feature (Progress: 40%)\n"
    )
    (coach_dir / "annual-goals.md").write_text("# 2026 Annual Goals\n\n1. Get promoted\n")
    return tmp_path


def test_read_existing_note():
    result = read_obsidian_note(note_path="coach/goals/quarterly-goals.md")
    assert "content" in result
    assert "Q1 OKRs" in result["content"]


def test_read_missing_note():
    result = read_obsidian_note(note_path="nonexistent.md")
    assert "error" in result
    assert "not found" in result["error"].lower()


def test_write_and_read_note(vault_dir):
    content = "# Daily Check-in\n\nPriorities: A, B, C\n"
    write_result = write_obsidian_note(
        note_path="coach/check-ins/daily/2026-02-13.md", content=content
    )
    assert write_result["status"] == "written"

    read_result = read_obsidian_note(note_path="coach/check-ins/daily/2026-02-13.md")
    assert read_result["content"] == content


def test_write_creates_parent_dirs(vault_dir):
    write_obsidian_note(note_path="deep/nested/dir/note.md", content="hello")
    assert (vault_dir / "deep" / "nested" / "dir" / "note.md").exists()


def test_list_notes():
    result = list_obsidian_notes(directory="coach/goals")
    assert result["count"] == 2
    paths = result["notes"]
    assert any("quarterly-goals.md" in p for p in paths)
    assert any("annual-goals.md" in p for p in paths)


def test_list_notes_missing_dir():
    result = list_obsidian_notes(directory="nonexistent")
    assert "error" in result


def test_search_vault():
    result = search_obsidian_vault(query="promoted")
    assert result["total_files_matched"] == 1
    assert "annual-goals.md" in result["results"][0]["path"]


def test_search_vault_scoped():
    result = search_obsidian_vault(query="KR1", directory="coach/goals")
    assert result["total_files_matched"] == 1


def test_search_vault_no_match():
    result = search_obsidian_vault(query="xyznonexistent")
    assert result["total_files_matched"] == 0


def test_path_traversal_blocked(vault_dir):
    result = read_obsidian_note(note_path="../../etc/passwd")
    assert "error" in result
