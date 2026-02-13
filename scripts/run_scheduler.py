#!/usr/bin/env python3
"""Start the scheduler for proactive daily/weekly check-ins."""

import asyncio
import signal
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env in the project root
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

from executive_coach.scheduler import CoachScheduler


def main() -> None:
    scheduler = CoachScheduler()
    scheduler.start()

    print("Executive Coach Scheduler is running.")
    print("Scheduled jobs:")
    for job in scheduler.scheduler.get_jobs():
        print(f"  - {job.id}: {job.trigger}")
    print("\nPress Ctrl+C to stop.\n")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    stop_event = asyncio.Event()

    def _shutdown(sig, frame):
        print("\nShutting down scheduler...")
        scheduler.stop()
        stop_event.set()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        loop.run_until_complete(stop_event.wait())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
