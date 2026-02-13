"""Accountability sub-agent: goal tracking, daily check-ins, weekly reviews."""

from google.adk.agents import LlmAgent

from executive_coach.prompts.accountability import ACCOUNTABILITY_PROMPT
from executive_coach.tools.obsidian import (
    read_obsidian_note,
    write_obsidian_note,
    list_obsidian_notes,
    search_obsidian_vault,
)
from executive_coach.tools.slack import send_slack_dm, send_slack_channel
from executive_coach.tools.utils import get_current_datetime

accountability_agent = LlmAgent(
    name="AccountabilityAgent",
    model="gemini-3-flash",
    description=(
        "Handles goal tracking, OKR check-ins, daily morning/evening check-ins, "
        "and weekly reviews. Delegate here for anything related to goals, "
        "progress, priorities, blockers, daily planning, or weekly reflection."
    ),
    instruction=ACCOUNTABILITY_PROMPT,
    tools=[
        read_obsidian_note,
        write_obsidian_note,
        list_obsidian_notes,
        search_obsidian_vault,
        send_slack_dm,
        send_slack_channel,
        get_current_datetime,
    ],
)
