"""Chat request/response schemas for the /chat endpoint."""

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """One user turn. Omit session_id to start a fresh conversation."""

    session_id: str | None = Field(
        default=None,
        description="Conversation id. Omit on the first message; reuse it to continue.",
    )
    message: str = Field(min_length=1)


class Widget(BaseModel):
    """A UI card derived from a tool result (rendered alongside the reply)."""

    type: str  # "policies" | "policy" | "claim" | "claim_status"
    data: dict[str, Any]


class ChatResponse(BaseModel):
    """The assistant reply, the session id to send back, and any UI widgets."""

    session_id: str
    reply: str
    widgets: list[Widget] = Field(default_factory=list)