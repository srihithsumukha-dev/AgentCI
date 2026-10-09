import json
from datetime import datetime, timezone
from pathlib import Path


class ToolRegistry:
    """Run only registered tools and record every tool-call attempt."""

    def __init__(self, allowed_tools, trace_path="traces/tool_calls.jsonl"):
        self.allowed_tools = set(allowed_tools)
        self.trace_path = Path(trace_path)
        self.tools = {}

    def register(self, name, function):
        self.tools[name] = function

    def call(self, tool_name, **kwargs):
        timestamp = datetime.now(timezone.utc).isoformat()

        if tool_name not in self.allowed_tools:
            result = {
                "ok": False,
                "error": f"Permission denied: {tool_name}",
            }
        elif tool_name not in self.tools:
            result = {
                "ok": False,
                "error": f"Unknown tool: {tool_name}",
            }
        else:
            try:
                value = self.tools[tool_name](**kwargs)
                result = {"ok": True, "result": value}
            except Exception as exc:
                result = {
                    "ok": False,
                    "error": f"Tool failed: {type(exc).__name__}: {exc}",
                }

        event = {
            "timestamp": timestamp,
            "tool": tool_name,
            "arguments": kwargs,
            **result,
        }

        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        with self.trace_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, default=str) + "\n")

        return result