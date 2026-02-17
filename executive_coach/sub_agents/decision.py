"""Decision sub-agent: Socratic coaching, frameworks, decision journaling."""

from google.adk.agents import LlmAgent

from executive_coach.prompts.decision import DECISION_PROMPT
from executive_coach.tools.obsidian import (
    read_obsidian_note,
    write_obsidian_note,
    search_obsidian_vault,
)
from executive_coach.tools.slack import send_slack_dm, send_slack_channel
from executive_coach.tools.utils import get_current_datetime, log_decision, get_decision_log

decision_agent = LlmAgent(
    name="DecisionAgent",
    model="gemini-3-flash-preview",
    description=(
        "Handles strategic decision support using Socratic questioning, "
        "structured frameworks (SWOT, decision matrix, pre-mortem), and "
        "decision journaling with outcome follow-up. Delegate here when the "
        "user is weighing options, facing a choice, or reviewing past decisions."
    ),
    instruction=DECISION_PROMPT,
    tools=[
        read_obsidian_note,
        write_obsidian_note,
        search_obsidian_vault,
        send_slack_dm,
        send_slack_channel,
        get_current_datetime,
        log_decision,
        get_decision_log,
    ],
)
