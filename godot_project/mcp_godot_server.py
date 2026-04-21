"""
MagicAI MCP Server - Godot 控制桥
将 godot_controller 的所有能力注册为 MCP 工具，
CodeBuddy / Cursor / Claude 等 Agent 可通过 JSON-RPC 直接操控 Godot。

启动: python mcp_godot_server.py
默认端口: 3000
"""

from __future__ import annotations
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable

import sys
sys.path.insert(0, os.path.dirname(__file__))
import godot_controller as godot

_TOOLS: dict[str, dict] = {}

def register(name: str, description: str, params: dict):
    def decorator(fn: Callable):
        _TOOLS[name] = {"fn": fn, "description": description, "params": params}
        return fn
    return decorator

@register("godot_ping", "测试与 Godot 编辑器的连接，返回版本信息", {})
def tool_ping(**_) -> dict: return godot.ping()

@register("godot_create_node", "在 Godot 当前打开的场景中创建一个节点",
    {"name": {"type": "string", "description": "节点名称"},
     "node_type": {"type": "string", "description": "节点类型 Node2D/Node3D/Label/Sprite2D", "default": "Node2D"}})
def tool_create_node(name: str, node_type: str = "Node2D", **_) -> dict:
    return godot.create_node(name, node_type)

@register("godot_delete_node", "删除 Godot 场景中指定名称的节点",
    {"name": {"type": "string", "description": "要删除的节点名称"}})
def tool_delete_node(name: str, **_) -> dict: return godot.delete_node(name)

@register("godot_list_nodes", "列出 Godot 当前场景的完整节点树", {})
def tool_list_nodes(**_) -> dict: return godot.list_nodes()

@register("godot_set_property", "设置 Godot 场景中某个节点的属性值",
    {"node": {"type": "string"}, "property": {"type": "string"}, "value": {"type": "any"}})
def tool_set_property(node: str, property: str, value: Any, **_) -> dict:
    return godot.set_property(node, property, value)

@register("godot_write_script", "将 GDScript 代码写入 Godot 项目指定路径",
    {"path": {"type": "string", "description": "res://scripts/xxx.gd"},
     "code": {"type": "string", "description": "完整 GDScript 代码"}})
def tool_write_script(path: str, code: str, **_) -> dict: return godot.write_script(path, code)

@register("godot_play", "在 Godot 编辑器中启动场景运行", {})
def tool_play(**_) -> dict: return godot.play()

@register("godot_stop", "停止 Godot 编辑器中正在运行的场景", {})
def tool_stop(**_) -> dict: return godot.stop()

@register("godot_save_scene", "保存 Godot 编辑器当前场景", {})
def tool_save_scene(**_) -> dict: return godot.save_scene()

@register("godot_build_scene", "批量创建节点，快速搭建场景结构",
    {"nodes": {"type": "array", "description": '[{"name":"Player","type":"Node2D"}]'}})
def tool_build_scene(nodes: list, **_) -> dict:
    results = [godot.create_node(n.get("name", "Node"), n.get("type", "Node2D")) for n in nodes]
    return {"ok": all(r.get("ok") for r in results), "results": results, "count": len(results)}


class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._respond({"tools": [{"name": n, "description": i["description"],
            "inputSchema": {"type": "object", "properties": i["params"]}} for n, i in _TOOLS.items()]})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self._respond(self._dispatch(json.loads(self.rfile.read(length))))

    def _dispatch(self, body: dict) -> dict:
        method, params, req_id = body.get("method",""), body.get("params",{}), body.get("id",1)
        if method == "tools/list":
            return {"jsonrpc":"2.0","id":req_id,"result":[{"name":n,"description":i["description"]} for n,i in _TOOLS.items()]}
        if method == "tools/call":
            t = _TOOLS.get(params.get("name",""))
            if not t: return {"jsonrpc":"2.0","id":req_id,"error":{"code":-32601,"message":"工具不存在"}}
            try: return {"jsonrpc":"2.0","id":req_id,"result":t["fn"](**params.get("arguments",{}))}
            except Exception as e: return {"jsonrpc":"2.0","id":req_id,"error":{"code":-32000,"message":str(e)}}
        return {"jsonrpc":"2.0","id":req_id,"error":{"code":-32601,"message":f"未知方法: {method}"}}

    def _respond(self, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",len(body)); self.end_headers(); self.wfile.write(body)

    def log_message(self, fmt, *args): print(f"[MCP] {fmt%args}")


def start(host="127.0.0.1", port=3000):
    print(f"[MagicAI MCP] http://{host}:{port}  工具: {list(_TOOLS.keys())}")
    HTTPServer((host, port), MCPHandler).serve_forever()

if __name__ == "__main__":
    start(os.environ.get("MCP_HOST","127.0.0.1"), int(os.environ.get("MCP_PORT",3000)))
