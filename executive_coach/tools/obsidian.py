"""Obsidian vault tools for reading, writing, listing, and searching notes."""

import os
from pathlib import Path


def _vault_path() -> Path:
    """Return the configured Obsidian vault path."""
    path = os.environ.get("OBSIDIAN_VAULT_PATH", "")
    if not path:
        raise RuntimeError("OBSIDIAN_VAULT_PATH environment variable is not set")
    return Path(path)


def _safe_resolve(base: Path, relative: str) -> Path:
    """Resolve a relative path safely within the vault base directory."""
    resolved = (base / relative).resolve()
    if not str(resolved).startswith(str(base.resolve())):
        raise ValueError(f"Path traversal detected: {relative}")
    return resolved


def read_obsidian_note(note_path: str) -> dict:
    """Read a note from the Obsidian vault.

    Args:
        note_path: Relative path to the note within the vault
                   (e.g. 'coach/goals/quarterly-goals.md').

    Returns:
        dict with 'content' (str) on success or 'error' (str) on failure.
    """
    try:
        vault = _vault_path()
        full_path = _safe_resolve(vault, note_path)
        if not full_path.exists():
            return {"error": f"Note not found: {note_path}"}
        content = full_path.read_text(encoding="utf-8")
        return {"content": content, "path": note_path}
    except Exception as e:
        return {"error": str(e)}


def write_obsidian_note(note_path: str, content: str) -> dict:
    """Create or update a note in the Obsidian vault.

    Args:
        note_path: Relative path for the note within the vault
                   (e.g. 'coach/check-ins/daily/2026-02-13.md').
        content: The full markdown content to write.

    Returns:
        dict with 'status' and 'path' on success or 'error' on failure.
    """
    try:
        vault = _vault_path()
        full_path = _safe_resolve(vault, note_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return {"status": "written", "path": note_path}
    except Exception as e:
        return {"error": str(e)}


def list_obsidian_notes(directory: str) -> dict:
    """List all markdown notes in a vault directory.

    Args:
        directory: Relative directory path within the vault
                   (e.g. 'coach/goals' or 'coach/check-ins/daily').

    Returns:
        dict with 'notes' (list of relative paths) or 'error'.
    """
    try:
        vault = _vault_path()
        full_dir = _safe_resolve(vault, directory)
        if not full_dir.is_dir():
            return {"error": f"Directory not found: {directory}"}
        notes = sorted(
            str(p.relative_to(vault))
            for p in full_dir.rglob("*.md")
            if p.is_file()
        )
        return {"notes": notes, "count": len(notes)}
    except Exception as e:
        return {"error": str(e)}


def search_obsidian_vault(query: str, directory: str = "") -> dict:
    """Full-text search across markdown notes in the vault.

    Args:
        query: Text to search for (case-insensitive substring match).
        directory: Optional relative directory to limit the search scope.
                   Searches the entire vault if empty.

    Returns:
        dict with 'results' (list of {path, matches}) or 'error'.
    """
    try:
        vault = _vault_path()
        search_root = _safe_resolve(vault, directory) if directory else vault
        if not search_root.is_dir():
            return {"error": f"Directory not found: {directory}"}

        query_lower = query.lower()
        results = []

        for md_file in search_root.rglob("*.md"):
            if not md_file.is_file():
                continue
            try:
                text = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            matching_lines = []
            for i, line in enumerate(text.splitlines(), start=1):
                if query_lower in line.lower():
                    matching_lines.append({"line": i, "text": line.strip()})

            if matching_lines:
                results.append(
                    {
                        "path": str(md_file.relative_to(vault)),
                        "matches": matching_lines[:10],  # cap per file
                    }
                )

        return {"results": results[:25], "total_files_matched": len(results)}
    except Exception as e:
        return {"error": str(e)}
