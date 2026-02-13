"""Utility tools: datetime, decision logging, and decision retrieval."""

import os
from datetime import datetime
from pathlib import Path


def _vault_path() -> Path:
    """Return the configured Obsidian vault path."""
    path = os.environ.get("OBSIDIAN_VAULT_PATH", "")
    if not path:
        raise RuntimeError("OBSIDIAN_VAULT_PATH environment variable is not set")
    return Path(path)


def get_current_datetime() -> dict:
    """Get the current date and time with useful scheduling context.

    Returns:
        dict with date, time, day_of_week, iso_week, and iso string.
    """
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "day_of_week": now.strftime("%A").lower(),
        "iso_week": f"{now.isocalendar().year}-W{now.isocalendar().week:02d}",
        "iso": now.isoformat(),
    }


def log_decision(
    title: str,
    context: str,
    options: str,
    analysis: str,
    decision: str,
    rationale: str,
    expected_outcome: str,
    review_date: str,
) -> dict:
    """Log a decision to the Obsidian decision journal.

    Args:
        title: Short title for the decision.
        context: Background and constraints.
        options: Options that were considered.
        analysis: Framework analysis (SWOT, decision matrix, pre-mortem, etc.).
        decision: The final decision made.
        rationale: Why this option was chosen.
        expected_outcome: What success looks like.
        review_date: Date to revisit this decision (YYYY-MM-DD).

    Returns:
        dict with 'status' and 'path' or 'error'.
    """
    try:
        vault = _vault_path()
        today = datetime.now().strftime("%Y-%m-%d")
        slug = title.lower().replace(" ", "-")[:50]
        filename = f"{today}-{slug}.md"
        decisions_dir = vault / "coach" / "decisions"
        decisions_dir.mkdir(parents=True, exist_ok=True)
        filepath = decisions_dir / filename

        content = f"""# Decision: {title}

**Date:** {today}
**Review Date:** {review_date}
**Status:** pending-review

## Context
{context}

## Options Considered
{options}

## Analysis
{analysis}

## Decision
{decision}

## Rationale
{rationale}

## Expected Outcome
{expected_outcome}

## Actual Outcome
_To be filled in on review date._
"""
        filepath.write_text(content, encoding="utf-8")
        rel_path = f"coach/decisions/{filename}"
        return {"status": "logged", "path": rel_path}
    except Exception as e:
        return {"error": str(e)}


def get_decision_log(status_filter: str = "") -> dict:
    """Retrieve past decisions from the decision journal.

    Args:
        status_filter: Optional filter — 'pending-review', 'reviewed', or
                       empty string for all decisions.

    Returns:
        dict with 'decisions' (list of {path, title, date, review_date, status})
        or 'error'.
    """
    try:
        vault = _vault_path()
        decisions_dir = vault / "coach" / "decisions"
        if not decisions_dir.is_dir():
            return {"decisions": [], "count": 0}

        decisions = []
        for md_file in sorted(decisions_dir.glob("*.md"), reverse=True):
            text = md_file.read_text(encoding="utf-8")
            lines = text.splitlines()

            title = ""
            date = ""
            review_date = ""
            status = ""

            for line in lines:
                if line.startswith("# Decision:"):
                    title = line.replace("# Decision:", "").strip()
                elif line.startswith("**Date:**"):
                    date = line.replace("**Date:**", "").strip()
                elif line.startswith("**Review Date:**"):
                    review_date = line.replace("**Review Date:**", "").strip()
                elif line.startswith("**Status:**"):
                    status = line.replace("**Status:**", "").strip()

            if status_filter and status != status_filter:
                continue

            decisions.append(
                {
                    "path": f"coach/decisions/{md_file.name}",
                    "title": title,
                    "date": date,
                    "review_date": review_date,
                    "status": status,
                }
            )

        return {"decisions": decisions[:50], "count": len(decisions)}
    except Exception as e:
        return {"error": str(e)}
