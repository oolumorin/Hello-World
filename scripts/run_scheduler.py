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


async def main() -> None:
    scheduler = CoachScheduler()
    scheduler.start()

    print("Executive Coach Scheduler is running.")
    print("Scheduled jobs:")
    for job in scheduler.scheduler.get_jobs():
        print(f"  - {job.id}: {job.trigger}")
    print("\nPress Ctrl+C to stop.\n")

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: (scheduler.stop(), stop_event.set()))

    await stop_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
