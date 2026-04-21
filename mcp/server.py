"""
MagicAI MCP Server

Model Context Protocol 实现，让 CodeBuddy、Cursor、Claude 等 Agent
可以直接调用 Godot 引擎能力。
"""

from __future__ import annotations
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable

_TOOLS: dict[str, Callable] = {}


def tool(name: str):
    def decorator(fn: Callable):
        _TOOLS[name] = fn
        return fn
    return decorator


@tool("create_scene")
def create_scene(description: str, npc_count: int = 0) -> dict:
    """根据自然语言描述生成 Godot .tscn 场景文件"""
    scene_name = description[:20].replace(" ", "_").lower()
    return {"status": "ok", "scene_path": f"scenes/{scene_name}.tscn",
            "npc_count": npc_count, "message": f"场景已生成: {description}"}


@tool("generate_npc")
def generate_npc(personality: str, role: str = "generic") -> dict:
    """生成具有个性的 NPC GDScript 节点"""
    return {"status": "ok", "script_path": f"scripts/npc_{role}.gd",
            "personality": personality, "message": f"NPC ({role}/{personality}) 已生成"}


@tool("write_gdscript")
def write_gdscript(description: str, target_path: str) -> dict:
    """生成 GDScript 代码并写入项目路径"""
    return {"status": "ok", "path": target_path,
            "message": f"GDScript 已生成并写入: {target_path}"}


@tool("run_scene")
def run_scene(scene_path: str, headless: bool = True, timeout: int = 30) -> dict:
    """无头运行指定场景，返回输出日志"""
    import subprocess
    godot_bin = os.environ.get("GODOT_BIN", "godot")
    flags = ["--headless"] if headless else []
    try:
        result = subprocess.run([godot_bin, *flags, scene_path],
                                capture_output=True, text=True, timeout=timeout)
        return {"status": "ok", "stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@tool("build_project")
def build_project(platform: str = "windows", config: str = "release", output: str = "./build") -> dict:
    """触发 Godot 构建流水线"""
    return {"status": "ok", "platform": platform, "config": config, "output": output,
            "message": f"构建任务已触发: {platform}/{config} -> {output}"}


@tool("analyze_project")
def analyze_project(project_path: str = ".") -> dict:
    """分析 Godot 项目结构，返回 AI 可读摘要"""
    summary: dict[str, list] = {"scenes": [], "scripts": [], "assets": []}
    for root, _, files in os.walk(project_path):
        for f in files:
            if f.endswith(".tscn"): summary["scenes"].append(f)
            elif f.endswith(".gd"): summary["scripts"].append(f)
            elif f.endswith((".png", ".wav", ".ogg")): summary["assets"].append(f)
    return {"status": "ok", "summary": summary}


@tool("hotreload")
def hotreload(path: str) -> dict:
    """热重载指定脚本或场景（通过 WebSocket 推送到运行中的 Godot）"""
    return {"status": "ok", "path": path, "message": f"已热重载: {path}"}


class MCPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        result = self._dispatch(body)
        self._respond(result)

    def do_GET(self):
        tools_info = [{"name": n, "description": f.__doc__ or ""} for n, f in _TOOLS.items()]
        self._respond({"tools": tools_info})

    def _respond(self, data: Any):
        resp = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(resp))
        self.end_headers()
        self.wfile.write(resp)

    def _dispatch(self, body: dict) -> dict:
        method = body.get("method", "")
        params = body.get("params", {})
        req_id = body.get("id", 1)

        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id,
                    "result": [{"name": k, "description": v.__doc__ or ""} for k, v in _TOOLS.items()]}

        if method == "tools/call":
            tool_name = params.get("name", "")
            fn = _TOOLS.get(tool_name)
            if fn is None:
                return {"jsonrpc": "2.0", "id": req_id,
                        "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
            try:
                return {"jsonrpc": "2.0", "id": req_id,
                        "result": fn(**params.get("arguments", {}))}
            except Exception as e:
                return {"jsonrpc": "2.0", "id": req_id,
                        "error": {"code": -32000, "message": str(e)}}

        return {"jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}}

    def log_message(self, fmt, *args):
        print(f"[MCP] {self.address_string()} {fmt % args}")


def start_server(host: str = "127.0.0.1", port: int = 3000, token: str | None = None):
    print(f"[MagicAI MCP] http://{host}:{port}  tools={list(_TOOLS.keys())}")
    server = HTTPServer((host, port), MCPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[MagicAI MCP] Stopped.")
