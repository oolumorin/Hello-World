"""Tests for Slack tools (mocked — no real Slack API calls)."""

import os
from unittest.mock import MagicMock, patch

import pytest

from executive_coach.tools.slack import (
    send_slack_dm,
    send_slack_channel,
    get_slack_history,
)


@pytest.fixture(autouse=True)
def slack_env(monkeypatch):
    """Set required Slack env vars."""
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")
    monkeypatch.setenv("SLACK_USER_ID", "U12345678")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "C12345678")


@patch("executive_coach.tools.slack.WebClient")
def test_send_slack_dm(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.conversations_open.return_value = {"channel": {"id": "D999"}}
    mock_client.chat_postMessage.return_value = {"ts": "1234567890.123456"}

    result = send_slack_dm(message="Hello from coach!")
    assert result["status"] == "sent"
    assert result["ts"] == "1234567890.123456"
    mock_client.chat_postMessage.assert_called_once_with(
        channel="D999", text="Hello from coach!"
    )


@patch("executive_coach.tools.slack.WebClient")
def test_send_slack_channel(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat_postMessage.return_value = {"ts": "1234567890.654321"}

    result = send_slack_channel(message="Weekly summary posted.")
    assert result["status"] == "sent"
    mock_client.chat_postMessage.assert_called_once_with(
        channel="C12345678", text="Weekly summary posted."
    )


@patch("executive_coach.tools.slack.WebClient")
def test_get_slack_history(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.conversations_open.return_value = {"channel": {"id": "D999"}}
    mock_client.conversations_history.return_value = {
        "messages": [
            {"user": "U12345678", "text": "Hi coach", "ts": "111"},
            {"user": "UBOT", "text": "Hello!", "ts": "112"},
        ]
    }

    result = get_slack_history(limit=10)
    assert result["count"] == 2
    assert result["messages"][0]["text"] == "Hi coach"


def test_send_dm_missing_user_id(monkeypatch):
    monkeypatch.delenv("SLACK_USER_ID", raising=False)
    result = send_slack_dm(message="test")
    assert "error" in result


def test_send_channel_missing_channel_id(monkeypatch):
    monkeypatch.delenv("SLACK_CHANNEL_ID", raising=False)
    result = send_slack_channel(message="test")
    assert "error" in result
