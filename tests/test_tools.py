import json

from agentci.tools import ToolRegistry


def test_allowed_tool_runs_and_is_traced(tmp_path):
    trace = tmp_path / "calls.jsonl"
    registry = ToolRegistry(["greet"], trace_path=trace)
    registry.register("greet", lambda name: f"Hello, {name}!")

    result = registry.call("greet", name="AgentCI")

    assert result == {"ok": True, "result": "Hello, AgentCI!"}

    event = json.loads(trace.read_text(encoding="utf-8").strip())
    assert event["tool"] == "greet"
    assert event["ok"] is True


def test_disallowed_tool_is_rejected_and_traced(tmp_path):
    trace = tmp_path / "calls.jsonl"
    registry = ToolRegistry([], trace_path=trace)
    registry.register("delete_files", lambda: "deleted")

    result = registry.call("delete_files")

    assert result["ok"] is False
    assert "Permission denied" in result["error"]

    event = json.loads(trace.read_text(encoding="utf-8").strip())
    assert event["tool"] == "delete_files"
    assert event["ok"] is False
def test_trace_records_multiple_calls_in_order(tmp_path):
    trace = tmp_path / "calls.jsonl"
    registry = ToolRegistry(["greet"], trace_path=trace)
    registry.register("greet", lambda name: f"Hello, {name}!")

    registry.call("greet", name="First")
    registry.call("unknown_tool")
    registry.call("greet", name="Second")

    events = [
        json.loads(line)
        for line in trace.read_text(encoding="utf-8").splitlines()
    ]

    assert len(events) == 3
    assert [event["tool"] for event in events] == [
        "greet",
        "unknown_tool",
        "greet",
    ]
    assert [event["ok"] for event in events] == [True, False, True]