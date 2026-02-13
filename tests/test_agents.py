"""Tests for agent definitions — verify agents are properly configured."""

from executive_coach.agent import root_agent
from executive_coach.sub_agents.accountability import accountability_agent
from executive_coach.sub_agents.decision import decision_agent
from executive_coach.sub_agents.career_coach import career_coach_agent


def test_root_agent_has_sub_agents():
    assert len(root_agent.sub_agents) == 3
    names = {a.name for a in root_agent.sub_agents}
    assert names == {"AccountabilityAgent", "DecisionAgent", "CareerCoachAgent"}


def test_root_agent_model():
    assert root_agent.model == "gemini-3-flash"


def test_root_agent_has_tools():
    assert len(root_agent.tools) > 0


def test_accountability_agent_config():
    assert accountability_agent.name == "AccountabilityAgent"
    assert accountability_agent.model == "gemini-3-flash"
    tool_names = [t.__name__ for t in accountability_agent.tools]
    assert "read_obsidian_note" in tool_names
    assert "send_slack_dm" in tool_names
    assert "get_current_datetime" in tool_names


def test_decision_agent_config():
    assert decision_agent.name == "DecisionAgent"
    assert decision_agent.model == "gemini-3-flash"
    tool_names = [t.__name__ for t in decision_agent.tools]
    assert "log_decision" in tool_names
    assert "get_decision_log" in tool_names


def test_career_coach_agent_config():
    assert career_coach_agent.name == "CareerCoachAgent"
    assert career_coach_agent.model == "gemini-3-flash"
    tool_names = [t.__name__ for t in career_coach_agent.tools]
    assert "read_obsidian_note" in tool_names
    assert "list_obsidian_notes" in tool_names
