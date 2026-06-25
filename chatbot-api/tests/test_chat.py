import json

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

import app.main as main


class FakeAgent:
    def __init__(self, messages=None, exc=None):
        self._messages = messages
        self._exc = exc

    async def ainvoke(self, inputs, config):
        if self._exc:
            raise self._exc
        return {"messages": self._messages}


@pytest.fixture
def client():
    return TestClient(main.app)


def _use(monkeypatch, agent):
    monkeypatch.setattr(main, "get_agent", lambda: agent)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_chat_happy(client, monkeypatch):
    _use(monkeypatch, FakeAgent([HumanMessage(content="hi"), AIMessage(content="Hello there!")]))
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"] == "Hello there!"
    assert body["session_id"]
    assert body["widgets"] == []


def test_session_reuse(client, monkeypatch):
    _use(monkeypatch, FakeAgent([HumanMessage(content="hi"), AIMessage(content="ok")]))
    r = client.post("/chat", json={"message": "hi", "session_id": "sess-test"})
    assert r.json()["session_id"] == "sess-test"


def test_empty_reply_fallback(client, monkeypatch):
    _use(monkeypatch, FakeAgent([HumanMessage(content="hi"), AIMessage(content="")]))
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert r.json()["reply"] == main._EMPTY_FALLBACK


def test_agent_error_returns_503(client, monkeypatch):
    _use(monkeypatch, FakeAgent(exc=RuntimeError("boom")))
    r = client.post("/chat", json={"message": "hi"})
    assert r.status_code == 503


def test_empty_message_422(client):
    assert client.post("/chat", json={"message": ""}).status_code == 422


def test_chat_emits_widget(client, monkeypatch):
    msgs = [
        HumanMessage(content="status of CLM-2026-00003"),
        ToolMessage(
            content=json.dumps({"claim_number": "CLM-2026-00003", "status": "submitted"}),
            name="check_claim_status", tool_call_id="t1",
        ),
        AIMessage(content="Your claim is submitted."),
    ]
    _use(monkeypatch, FakeAgent(msgs))
    body = client.post("/chat", json={"message": "status?"}).json()
    assert body["reply"] == "Your claim is submitted."
    assert len(body["widgets"]) == 1
    assert body["widgets"][0]["type"] == "claim_status"
    assert body["widgets"][0]["data"]["claim_number"] == "CLM-2026-00003"