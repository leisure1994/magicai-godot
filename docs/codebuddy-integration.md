# CodeBuddy 深度集成指南

MagicAI 通过 MCP 协议与 CodeBuddy 深度协同，让 AI 编程 Agent 直接操控 Godot 引擎。

## 1. 启动 MCP Server

```bash
magicai mcp serve --port 3000
```

## 2. 在 CodeBuddy 中配置 MCP

打开 CodeBuddy → 设置 → MCP 服务器，添加：

```json
{
  "name": "magicai-godot",
  "url": "http://127.0.0.1:3000"
}
```

## 3. 可用工具

| 工具 | 参数 | 描述 |
|------|------|------|
| `create_scene` | `description`, `npc_count` | 生成 .tscn 场景 |
| `generate_npc` | `personality`, `role` | 生成 NPC 节点 |
| `write_gdscript` | `description`, `target_path` | 生成并写入脚本 |
| `run_scene` | `scene_path`, `headless` | 无头运行场景 |
| `build_project` | `platform`, `config`, `output` | 触发构建 |
| `analyze_project` | `project_path` | 分析项目结构 |
| `hotreload` | `path` | 热重载脚本/场景 |

## 4. 工作流示例

> 在 CodeBuddy 中输入：
> "帮我创建中世纪市集场景，含3个商人NPC，并生成对话脚本"

CodeBuddy 自动调用链：
1. `create_scene` → 生成场景框架
2. `generate_npc` × 3 → 生成3个商人
3. `write_gdscript` → 生成对话逻辑
4. `hotreload` → 热重载到编辑器

## 5. 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MAGICAI_MODEL` | 默认 LLM | `gpt-4o` |
| `MAGICAI_MCP_TOKEN` | MCP Token | 空 |
| `MAGICAI_PROXY_PORT` | 推理代理端口 | `7788` |
| `GODOT_BIN` | Godot 路径 | `godot` |
| `OPENAI_API_KEY` | OpenAI Key | — |
