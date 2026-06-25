"""FastAPI entrypoint for the chatbot service."""

import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from app.agent import get_agent
from app.config import get_settings
from app.schemas import ChatRequest, ChatResponse
from app.tools import client as insurance_client
from app.widgets import widgets_for_turn

logger = logging.getLogger("chatbot")

_FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
_EMPTY_FALLBACK = "Sorry, I did not catch that. Could you rephrase or try again?"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Close the pooled HTTP client to the insurance API on shutdown.
    await insurance_client.aclose()


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)

_origins = (
    ["*"] if settings.cors_allow_origins.strip() == "*"
    else [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _reply_text(message: BaseMessage) -> str:
    """Flatten an assistant message (a plain string OR a list of content
    blocks, which is what Gemini returns when it includes reasoning) to text."""
    content = message.content
    if isinstance(content, str):
        return content.strip()
    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
    return "".join(parts).strip()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/")
async def index() -> FileResponse:
    """Serve the single-page chat UI."""
    return FileResponse(_FRONTEND)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    # The session id is reused as the LangGraph thread_id, so the checkpointer
    # restores this conversation history. Mint one if the client did not send it.
    session_id = request.session_id or str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": session_id}}

    agent = get_agent()
    try:
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=request.message)]},
            config,
        )
    except Exception as exc:
        logger.exception("Agent invocation failed")
        raise HTTPException(
            status_code=503,
            detail="The assistant is temporarily unavailable (the language model "
                   "may be rate-limited). Please try again in a moment.",
        ) from exc

    messages = result["messages"]
    reply = _reply_text(messages[-1]) or _EMPTY_FALLBACK
    return ChatResponse(
        session_id=session_id,
        reply=reply,
        widgets=widgets_for_turn(messages),
    )