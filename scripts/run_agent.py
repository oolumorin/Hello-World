#!/usr/bin/env python3
"""Start the executive coach agent in interactive mode via ADK CLI."""

import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env in the project root
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")


def main() -> None:
    """Launch the agent using `adk run`."""
    # adk run expects the agent package directory
    agent_dir = str(project_root / "executive_coach")
    cmd = [sys.executable, "-m", "google.adk.cli", "run", agent_dir]

    print("Starting Executive Coach Agent (interactive mode)...")
    print("Type your messages below. Press Ctrl+C to exit.\n")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
