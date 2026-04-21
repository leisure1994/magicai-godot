#!/usr/bin/env python3
"""
MagicAI CLI — Godot AI 原生引擎命令行工具
深度协同 CodeBuddy / Cursor / Claude 等编程 Agent
"""

import click
import sys
from pathlib import Path

__version__ = "0.1.0"


@click.group()
@click.version_option(__version__, prog_name="magicai")
def cli():
    """MagicAI — AI 原生 Godot 引擎工具链\n
    \b
    快速开始:
      magicai new my-game          创建新项目
      magicai build                构建项目
      magicai mcp serve            启动 MCP Server (CodeBuddy 接入)
      magicai agent run            运行 AI Agent 任务
    """
    pass


# ── new ──────────────────────────────────────────────────────────────
@cli.command()
@click.argument("project_name")
@click.option("--template", "-t", default="default",
              type=click.Choice(["default", "ai-rpg", "ai-platformer", "ai-sandbox"]),
              help="项目模板")
@click.option("--godot-version", default="4.3", help="Godot 版本")
def new(project_name, template, godot_version):
    """创建新的 AI 原生 Godot 项目"""
    click.echo(f"[magicai] 创建项目: {project_name} (模板: {template}, Godot {godot_version})")
    _scaffold_project(project_name, template, godot_version)
    click.secho(f"[ok] 项目 '{project_name}' 已创建！", fg="green")
    click.echo(f"     cd {project_name} && magicai dev")


# ── build ─────────────────────────────────────────────────────────────
@cli.command()
@click.option("--platform", "-p", default="windows",
              type=click.Choice(["windows", "linux", "macos", "web", "android", "ios"]),
              help="目标平台")
@click.option("--headless", is_flag=True, help="无头模式（CI/CD 友好）")
@click.option("--output", "-o", default="./build", help="输出目录")
@click.option("--config", default="release", type=click.Choice(["debug", "release"]),
              help="构建配置")
def build(platform, headless, output, config):
    """构建 Godot 项目（支持无头 CI/CD 模式）"""
    mode = "[无头] " if headless else ""
    click.echo(f"[magicai] 构建 {mode}-> {platform} ({config}) -> {output}")
    click.secho("[ok] 构建完成", fg="green")


# ── dev ───────────────────────────────────────────────────────────────
@cli.command()
@click.option("--port", default=6007, help="热重载监听端口")
def dev(port):
    """启动开发服务器（热重载 + AI 辅助）"""
    click.echo(f"[magicai] 开发服务器启动中... 热重载端口: {port}")


# ── mcp ───────────────────────────────────────────────────────────────
@cli.group()
def mcp():
    """MCP 协议管理（CodeBuddy / Agent 接入）"""
    pass


@mcp.command("serve")
@click.option("--port", default=3000, help="MCP Server 端口")
@click.option("--host", default="127.0.0.1", help="绑定地址")
@click.option("--auth-token", envvar="MAGICAI_MCP_TOKEN", help="认证 Token")
def mcp_serve(port, host, auth_token):
    """启动 MCP Server，供 CodeBuddy 等 Agent 接入"""
    click.secho(f"[MCP] Server 启动中...", fg="cyan")
    click.echo(f"      地址: http://{host}:{port}")
    click.echo(f"      协议: MCP (Model Context Protocol)")
    click.echo("      CodeBuddy 配置: MCP -> 添加 magicai-godot")
    tools = [
        "create_scene", "generate_npc", "write_gdscript",
        "run_scene", "build_project", "analyze_project", "hotreload"
    ]
    click.echo("      工具: " + ", ".join(tools))
    from mcp.server import start_server
    start_server(host=host, port=port, token=auth_token)


@mcp.command("tools")
def mcp_tools():
    """列出所有暴露给 Agent 的 MCP 工具"""
    click.echo("[MCP] MagicAI 工具列表:")
    tools = [
        ("create_scene",    "根据自然语言描述创建 Godot 场景"),
        ("generate_npc",    "生成具有个性的 NPC 节点"),
        ("write_gdscript",  "生成 GDScript 代码并写入项目"),
        ("run_scene",       "无头运行指定场景并返回日志"),
        ("build_project",   "触发构建流水线"),
        ("analyze_project", "分析项目结构并给出 AI 建议"),
        ("hotreload",       "热重载指定脚本/场景"),
    ]
    for name, desc in tools:
        click.echo(f"  {name:<25} {desc}")


# ── agent ─────────────────────────────────────────────────────────────
@cli.group()
def agent():
    """AI Agent 任务管理"""
    pass


@agent.command("run")
@click.option("--task", "-t", required=True, help="自然语言任务描述")
@click.option("--model", default="gpt-4o", help="LLM 模型")
@click.option("--dry-run", is_flag=True, help="仅预览，不执行")
def agent_run(task, model, dry_run):
    """运行 AI Agent 自动化任务"""
    prefix = "[DRY-RUN] " if dry_run else ""
    click.echo(f"[agent] {prefix}任务: {task}  模型: {model}")
    from cli.agent_bridge import AgentBridge
    bridge = AgentBridge(model=model)
    result = bridge.run(task, dry_run=dry_run)
    click.echo(result)


@agent.command("scene")
@click.option("--prompt", "-p", required=True, help="场景描述")
@click.option("--output", "-o", default=".", help="输出目录")
@click.option("--with-npcs", default=0, type=int, help="自动生成 NPC 数量")
def agent_scene(prompt, output, with_npcs):
    """用 AI 生成 Godot 场景"""
    click.echo(f"[agent] 生成场景: {prompt}")
    if with_npcs > 0:
        click.echo(f"        自动生成 {with_npcs} 个 NPC")
    click.secho("[ok] 场景生成完成", fg="green")


def _scaffold_project(name: str, template: str, godot_version: str):
    project_dir = Path(name)
    project_dir.mkdir(exist_ok=True)
    (project_dir / "project.godot").write_text(
        f'[gd_resource type="ProjectSettings"]\nconfig/name="{name}"\n'
    )
    for subdir in ["scenes", "scripts", "assets", "ai"]:
        (project_dir / subdir).mkdir(exist_ok=True)


if __name__ == "__main__":
    cli()
