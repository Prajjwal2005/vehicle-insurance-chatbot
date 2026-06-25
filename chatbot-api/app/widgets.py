"""Derive UI widgets from the tool results produced during a single turn.

The agent calls tools whose results are JSON. We turn the useful ones into small
structured widgets the frontend renders as cards, so the user sees a plan
comparison / receipt / status badge instead of only prose.
"""

import json
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage

from app.schemas import Widget


def _safe_json(text: object) -> Any:
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


def widgets_for_turn(messages: list[BaseMessage]) -> list[Widget]:
    """Build widgets from the ToolMessages produced since the last user message."""
    start = 0
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], HumanMessage):
            start = i
            break

    widgets: list[Widget] = []
    for msg in messages[start:]:
        if not isinstance(msg, ToolMessage):
            continue
        data = _safe_json(msg.content)
        if data is None or (isinstance(data, dict) and "error" in data):
            continue
        name = msg.name or ""
        if name == "list_policies" and isinstance(data, list):
            widgets.append(Widget(type="policies", data={"plans": data}))
        elif name == "confirm_application" and isinstance(data, dict):
            widgets.append(Widget(type="policy", data=data))
        elif name == "confirm_claim" and isinstance(data, dict):
            widgets.append(Widget(type="claim", data=data))
        elif name == "check_claim_status" and isinstance(data, dict):
            widgets.append(Widget(type="claim_status", data=data))
    return widgets