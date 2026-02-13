#!/usr/bin/env python3
"""Slack Bolt app that bridges Slack events to the ADK executive coach agent."""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from executive_coach.agent import root_agent

# --- ADK Runner setup ---
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="executive_coach",
    session_service=session_service,
)

# Track Slack user → ADK session mapping
_user_sessions: dict[str, str] = {}

# --- Slack Bolt app ---
app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])


async def _get_or_create_session(slack_user_id: str) -> str:
    """Get an existing ADK session ID for a Slack user, or create one."""
    if slack_user_id not in _user_sessions:
        session = await session_service.create_session(
            app_name="executive_coach",
            user_id=slack_user_id,
        )
        _user_sessions[slack_user_id] = session.id
    return _user_sessions[slack_user_id]


async def _run_agent(user_id: str, text: str) -> str:
    """Send a message to the ADK agent and collect the response."""
    session_id = await _get_or_create_session(user_id)
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=text)],
    )

    response_parts: list[str] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_parts.append(part.text)

    return "\n".join(response_parts) if response_parts else "I'm here! How can I help?"


@app.event("message")
async def handle_dm(event, say):
    """Handle direct messages sent to the bot."""
    # Ignore bot messages to prevent loops
    if event.get("bot_id") or event.get("subtype"):
        return

    user_id = event["user"]
    text = event.get("text", "")
    if not text.strip():
        return

    response = await _run_agent(user_id, text)

    # Slack has a 4000 char limit per message — chunk if needed
    max_len = 3900
    while response:
        chunk = response[:max_len]
        response = response[max_len:]
        await say(text=chunk)


@app.event("app_mention")
async def handle_mention(event, say):
    """Handle @mentions of the bot in channels."""
    user_id = event["user"]
    text = event.get("text", "")
    if not text.strip():
        return

    response = await _run_agent(user_id, text)

    max_len = 3900
    while response:
        chunk = response[:max_len]
        response = response[max_len:]
        await say(text=chunk)


async def main():
    """Start the Slack bot in Socket Mode."""
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("Executive Coach Slack bot is running in Socket Mode...")
    print("Press Ctrl+C to stop.\n")
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
