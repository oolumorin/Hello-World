"""Slack tools for sending and reading messages."""

import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def _slack_client() -> WebClient:
    """Return a configured Slack WebClient."""
    token = os.environ.get("SLACK_BOT_TOKEN", "")
    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN environment variable is not set")
    return WebClient(token=token)


def send_slack_dm(message: str) -> dict:
    """Send a direct message to the user on Slack.

    Args:
        message: The message text to send (supports Slack mrkdwn formatting).

    Returns:
        dict with 'status' and 'ts' (message timestamp) or 'error'.
    """
    try:
        client = _slack_client()
        user_id = os.environ.get("SLACK_USER_ID", "")
        if not user_id:
            return {"error": "SLACK_USER_ID environment variable is not set"}

        # Open or retrieve the DM channel
        response = client.conversations_open(users=[user_id])
        channel_id = response["channel"]["id"]

        result = client.chat_postMessage(channel=channel_id, text=message)
        return {"status": "sent", "ts": result["ts"], "channel": channel_id}
    except SlackApiError as e:
        return {"error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"error": str(e)}


def send_slack_channel(message: str) -> dict:
    """Post a message to the #coach-log channel on Slack.

    Args:
        message: The message text to post (supports Slack mrkdwn formatting).

    Returns:
        dict with 'status' and 'ts' or 'error'.
    """
    try:
        client = _slack_client()
        channel_id = os.environ.get("SLACK_CHANNEL_ID", "")
        if not channel_id:
            return {"error": "SLACK_CHANNEL_ID environment variable is not set"}

        result = client.chat_postMessage(channel=channel_id, text=message)
        return {"status": "sent", "ts": result["ts"], "channel": channel_id}
    except SlackApiError as e:
        return {"error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"error": str(e)}


def get_slack_history(limit: int = 20) -> dict:
    """Read recent DM conversation history with the user.

    Args:
        limit: Maximum number of messages to retrieve (default 20, max 100).

    Returns:
        dict with 'messages' (list of {user, text, ts}) or 'error'.
    """
    try:
        client = _slack_client()
        user_id = os.environ.get("SLACK_USER_ID", "")
        if not user_id:
            return {"error": "SLACK_USER_ID environment variable is not set"}

        limit = min(max(1, limit), 100)

        response = client.conversations_open(users=[user_id])
        channel_id = response["channel"]["id"]

        history = client.conversations_history(channel=channel_id, limit=limit)
        messages = [
            {
                "user": msg.get("user", "bot"),
                "text": msg.get("text", ""),
                "ts": msg.get("ts", ""),
            }
            for msg in history.get("messages", [])
        ]
        return {"messages": messages, "count": len(messages)}
    except SlackApiError as e:
        return {"error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"error": str(e)}
