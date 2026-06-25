"""Chat request/response schemas for the /chat endpoint."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """One user turn. Omit session_id to start a fresh conversation."""

    session_id: str | None = Field(
        default=None,
        description="Conversation id. Omit on the first message; reuse it to continue.",
    )
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    """The assistant's reply, plus the session id to send back next turn."""

    session_id: str
    reply: str