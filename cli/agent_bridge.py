"""
AgentBridge — CodeBuddy / Cursor / Claude 等 Agent 协同桥接
通过 MCP 协议暴露 Godot 引擎能力给外部 AI Agent。
"""

from __future__ import annotations
import json
from typing import Any


class AgentBridge:
    """统一的 Agent 协同接口"""

    def __init__(self, model: str = "gpt-4o", mcp_url: str = "http://127.0.0.1:3000"):
        self.model = model
        self.mcp_url = mcp_url

    def run(self, task: str, dry_run: bool = False) -> str:
        """以自然语言描述执行引擎任务，Agent 自动规划工具调用链"""
        plan = self._plan(task)
        if dry_run:
            return self._format_plan(plan)
        return self._execute_plan(plan)

    def create_scene(self, description: str, npc_count: int = 0) -> dict[str, Any]:
        return self._call_mcp_tool("create_scene", {"description": description, "npc_count": npc_count})

    def generate_npc(self, personality: str, role: str = "generic") -> dict[str, Any]:
        return self._call_mcp_tool("generate_npc", {"personality": personality, "role": role})

    def write_gdscript(self, description: str, target_path: str) -> dict[str, Any]:
        return self._call_mcp_tool("write_gdscript", {"description": description, "target_path": target_path})

    def hotreload(self, path: str) -> dict[str, Any]:
        return self._call_mcp_tool("hotreload", {"path": path})

    def _call_mcp_tool(self, tool: str, params: dict) -> dict[str, Any]:
        import urllib.request
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                               "params": {"name": tool, "arguments": params}}).encode()
        req = urllib.request.Request(self.mcp_url, data=payload,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e), "tool": tool}

    def _plan(self, task: str) -> list[dict]:
        return [{"tool": "analyze_project", "reason": f"理解上下文以完成: {task}"}]

    def _execute_plan(self, plan: list[dict]) -> str:
        return "\n".join(
            f"[{s['tool']}] {self._call_mcp_tool(s['tool'], s.get('params', {}))}"
            for s in plan
        )

    def _format_plan(self, plan: list[dict]) -> str:
        return "\n".join(
            ["[DRY-RUN] 规划的工具调用链:"] +
            [f"  {i}. {s['tool']} — {s.get('reason', '')}" for i, s in enumerate(plan, 1)]
        )
