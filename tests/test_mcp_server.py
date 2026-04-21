"""
MCP Server 基础功能测试
"""
import json
import threading
import time
import urllib.request
import pytest


def test_mcp_tools_import():
    from mcp.server import _TOOLS
    expected = {"create_scene", "generate_npc", "write_gdscript",
                "run_scene", "build_project", "analyze_project", "hotreload"}
    assert expected.issubset(set(_TOOLS.keys()))


def test_create_scene():
    from mcp.server import create_scene
    result = create_scene("测试场景", npc_count=2)
    assert result["status"] == "ok"
    assert "scene_path" in result


def test_generate_npc():
    from mcp.server import generate_npc
    result = generate_npc("friendly", "merchant")
    assert result["status"] == "ok"
    assert "script_path" in result


def test_analyze_project(tmp_path):
    from mcp.server import analyze_project
    (tmp_path / "scene.tscn").write_text("")
    (tmp_path / "player.gd").write_text("")
    result = analyze_project(str(tmp_path))
    assert result["status"] == "ok"
    assert "scene.tscn" in result["summary"]["scenes"]
    assert "player.gd" in result["summary"]["scripts"]
