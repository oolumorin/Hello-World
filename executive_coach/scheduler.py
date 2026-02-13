"""APScheduler-based scheduler for proactive daily/weekly check-ins."""

import asyncio
import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from executive_coach.agent import root_agent


def _parse_time(env_var: str, default: str) -> tuple[int, int]:
    """Parse a HH:MM time string from an environment variable."""
    raw = os.environ.get(env_var, default)
    parts = raw.strip().split(":")
    return int(parts[0]), int(parts[1])


class CoachScheduler:
    """Manages scheduled check-ins via APScheduler and the ADK runner."""

    def __init__(self) -> None:
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=root_agent,
            app_name="executive_coach",
            session_service=self.session_service,
        )
        self.scheduler = AsyncIOScheduler()
        self._user_id = "coach-user"

    async def _run_agent(self, prompt: str) -> str:
        """Send a prompt to the agent and collect the response."""
        session = await self.session_service.create_session(
            app_name="executive_coach",
            user_id=self._user_id,
        )

        from google.genai import types

        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )

        response_parts: list[str] = []
        async for event in self.runner.run_async(
            user_id=self._user_id,
            session_id=session.id,
            new_message=user_content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_parts.append(part.text)

        return "\n".join(response_parts)

    async def morning_checkin(self) -> None:
        """Trigger the morning check-in."""
        today = datetime.now().strftime("%Y-%m-%d")
        prompt = (
            f"It's the morning of {today}. Please run the morning check-in: "
            "review my daily note if it exists, read my current quarterly goals, "
            "and send me a Slack DM asking about my top 3 priorities for today. "
            "Post a brief summary to #coach-log."
        )
        await self._run_agent(prompt)

    async def evening_checkin(self) -> None:
        """Trigger the evening reflection."""
        today = datetime.now().strftime("%Y-%m-%d")
        prompt = (
            f"It's the evening of {today}. Please run the evening reflection: "
            "send me a Slack DM asking what I accomplished today and any blockers. "
            "Log the check-in to the daily check-in note."
        )
        await self._run_agent(prompt)

    async def weekly_review(self) -> None:
        """Trigger the weekly review."""
        prompt = (
            "It's time for the weekly review. Please aggregate this week's "
            "daily check-ins, review OKR progress compared to last week, "
            "generate a structured weekly summary, write it to the weekly "
            "check-in note, post it to #coach-log, and send me a Slack DM "
            "asking for my reflection on the week."
        )
        await self._run_agent(prompt)

    def start(self) -> None:
        """Configure and start the scheduler."""
        morning_h, morning_m = _parse_time("MORNING_CHECKIN_TIME", "09:00")
        evening_h, evening_m = _parse_time("EVENING_CHECKIN_TIME", "17:30")
        review_day = os.environ.get("WEEKLY_REVIEW_DAY", "friday").strip().lower()[:3]
        review_h, review_m = _parse_time("WEEKLY_REVIEW_TIME", "14:00")

        self.scheduler.add_job(
            self.morning_checkin,
            "cron",
            hour=morning_h,
            minute=morning_m,
            day_of_week="mon-fri",
            id="morning_checkin",
        )
        self.scheduler.add_job(
            self.evening_checkin,
            "cron",
            hour=evening_h,
            minute=evening_m,
            day_of_week="mon-fri",
            id="evening_checkin",
        )
        self.scheduler.add_job(
            self.weekly_review,
            "cron",
            hour=review_h,
            minute=review_m,
            day_of_week=review_day,
            id="weekly_review",
        )

        self.scheduler.start()

    def stop(self) -> None:
        """Shut down the scheduler."""
        self.scheduler.shutdown(wait=False)
