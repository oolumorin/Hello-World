"""Career Coach sub-agent: career planning, skill gaps, promotion readiness."""

from google.adk.agents import LlmAgent

from executive_coach.prompts.career_coach import CAREER_COACH_PROMPT
from executive_coach.tools.obsidian import (
    read_obsidian_note,
    write_obsidian_note,
    list_obsidian_notes,
    search_obsidian_vault,
)
from executive_coach.tools.slack import send_slack_dm, send_slack_channel
from executive_coach.tools.utils import get_current_datetime

career_coach_agent = LlmAgent(
    name="CareerCoachAgent",
    model="gemini-3-flash",
    description=(
        "Handles career growth coaching including career planning, skill gap "
        "analysis, promotion readiness tracking, networking strategy, and "
        "IC-vs-management path exploration. Delegate here for career trajectory, "
        "skills, promotions, visibility, or professional development."
    ),
    instruction=CAREER_COACH_PROMPT,
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
