"""The LangGraph agent: Gemini + insurance tools + conversation memory."""

from datetime import datetime
from functools import lru_cache

from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from app.config import get_settings
from app.prompts import SYSTEM_PROMPT
from app.tools import TOOLS


def _prompt(state: dict) -> list:
    """Build the message list for the model, with a freshly-dated system prompt.

    create_react_agent calls this every turn, so the current date/time is always
    accurate - no staleness on a long-running server.
    """
    now = datetime.now().strftime("%A, %Y-%m-%d %H:%M")
    system = f"{SYSTEM_PROMPT}\n\nFor reference, the current date and time is {now}."
    return [SystemMessage(content=system), *state["messages"]]


def _build_model(settings):
    """Primary model with a fallback to a second one when the primary fails.

    The Gemini free tier limits per-minute requests per model. By falling back to
    a second model on rate-limit / availability errors, we get a second RPM
    bucket for free and recover gracefully mid-conversation.
    """
    primary = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0,
        max_retries=2,
    )
    if not settings.gemini_fallback_model or settings.gemini_fallback_model == settings.gemini_model:
        return primary
    backup = ChatGoogleGenerativeAI(
        model=settings.gemini_fallback_model,
        google_api_key=settings.google_api_key,
        temperature=0,
        max_retries=2,
    )
    return primary.with_fallbacks([backup])


@lru_cache
def get_agent():
    """Build the agent once and reuse it (the checkpointer holds all sessions).

    The checkpointer is MemorySaver for local dev; the production swap is a
    persistent checkpointer (e.g. langgraph-checkpoint-postgres) - see
    docs/design.md.
    """
    settings = get_settings()
    return create_react_agent(
        _build_model(settings),
        tools=TOOLS,
        prompt=_prompt,
        checkpointer=MemorySaver(),
    )