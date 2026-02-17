"""Root coordinator agent for the Executive Coach."""

from google.adk.agents import LlmAgent

from executive_coach.prompts.coordinator import COORDINATOR_PROMPT
from executive_coach.sub_agents.accountability import accountability_agent
from executive_coach.sub_agents.decision import decision_agent
from executive_coach.sub_agents.career_coach import career_coach_agent
from executive_coach.tools.obsidian import (
    read_obsidian_note,
    write_obsidian_note,
    list_obsidian_notes,
    search_obsidian_vault,
)
from executive_coach.tools.slack import (
    send_slack_dm,
    send_slack_channel,
    get_slack_history,
)
from executive_coach.tools.utils import get_current_datetime

root_agent = LlmAgent(
    name="ExecutiveCoach",
    model="gemini-3-flash-preview",
    description="Executive coach coordinator that routes to specialist sub-agents.",
    instruction=COORDINATOR_PROMPT,
    tools=[
        read_obsidian_note,
        write_obsidian_note,
        list_obsidian_notes,
        search_obsidian_vault,
        send_slack_dm,
        send_slack_channel,
        get_slack_history,
        get_current_datetime,
    ],
    sub_agents=[
        accountability_agent,
        decision_agent,
        career_coach_agent,
    ],
)
