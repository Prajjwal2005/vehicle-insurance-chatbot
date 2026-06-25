"""The LangGraph agent: Gemini + insurance tools + conversation memory.

create_react_agent wires the standard model<->tools loop. The MemorySaver
checkpointer gives each conversation its own remembered history, keyed by the
thread_id we pass in the run config when invoking the agent.
"""

from datetime import datetime
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from app.config import get_settings
from app.prompts import SYSTEM_PROMPT
from app.tools import TOOLS


@lru_cache
def get_agent():
    """Build the agent once and reuse it (the checkpointer holds all sessions)."""
    settings = get_settings()
    model = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0,
        max_retries=2,
    )
    # Give the model the current date so it can resolve "yesterday", "3pm", etc.
    # Injected at build time; a long-running server would refresh this per request
    # (via a callable prompt) so it never goes stale.
    now = datetime.now().strftime("%A, %Y-%m-%d %H:%M")
    prompt = f"{SYSTEM_PROMPT}\n\nFor reference, the current date and time is {now}."
    return create_react_agent(
        model,
        tools=TOOLS,
        prompt=prompt,
        checkpointer=MemorySaver(),
    )