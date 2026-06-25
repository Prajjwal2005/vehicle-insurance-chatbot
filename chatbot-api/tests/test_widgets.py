import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.widgets import widgets_for_turn


def _tool(name, payload):
    return ToolMessage(content=json.dumps(payload), name=name, tool_call_id="t")


def test_policies_widget():
    msgs = [
        HumanMessage(content="apply"),
        AIMessage(content="ok"),
        _tool("list_policies", [
            {"id": 2, "name": "Full Coverage Standard", "price": 1200, "features": ["a", "b"]},
        ]),
        AIMessage(content="here are the plans"),
    ]
    widgets = widgets_for_turn(msgs)
    assert len(widgets) == 1
    assert widgets[0].type == "policies"
    assert widgets[0].data["plans"][0]["name"] == "Full Coverage Standard"


def test_policy_receipt_widget():
    msgs = [
        HumanMessage(content="yes"),
        _tool("confirm_application", {"policy_number": "POL-2026-00006", "status": "submitted"}),
        AIMessage(content="done"),
    ]
    w = widgets_for_turn(msgs)
    assert w[0].type == "policy"
    assert w[0].data["policy_number"] == "POL-2026-00006"


def test_status_widget():
    msgs = [
        HumanMessage(content="status"),
        _tool("check_claim_status", {"claim_number": "CLM-2026-00003", "status": "submitted"}),
        AIMessage(content="..."),
    ]
    w = widgets_for_turn(msgs)
    assert w[0].type == "claim_status"


def test_error_tool_produces_no_widget():
    msgs = [
        HumanMessage(content="x"),
        _tool("check_claim_status", {"error": "not found"}),
        AIMessage(content="..."),
    ]
    assert widgets_for_turn(msgs) == []


def test_previous_turn_ignored():
    msgs = [
        _tool("list_policies", [{"id": 1, "name": "Old", "price": 1, "features": []}]),
        HumanMessage(content="new turn"),
        AIMessage(content="hi"),
    ]
    assert widgets_for_turn(msgs) == []