# MagicAI (Godot) — AI 原生引擎架构

> **引擎完成 CLI 化改造 · 深度协同 CodeBuddy 等编程 Agent**

## 项目愿景

MagicAI 是基于 Godot 引擎的 **AI 原生游戏引擎架构**，将 LLM / Agent 能力作为引擎一等公民深度内嵌，实现：

- 🧠 **AI 原生**：GDScript / C# 内置 `AINode`、`AIBehavior`、`AIWorld` 等原生节点
- ⌨️ **CLI 化**：完整命令行工具链，支持无头构建、Agent 驱动自动化
- 🤝 **Agent 协同**：通过 MCP 协议与 CodeBuddy、Cursor、Claude 等编程 Agent 深度集成
- 🔄 **实时推理**：游戏运行时 LLM 推理、NPC 行为生成、剧情动态演化

---

## 架构概览

```
magicai-godot/
├── cli/                    # CLI 工具链 (magicai 命令)
│   ├── magicai.py          # 主入口
│   ├── commands/           # 子命令模块
│   └── agent_bridge.py     # Agent 协同桥接
├── engine/                 # 引擎扩展核心
│   ├── ai_nodes/           # AI 原生节点 (GDScript)
│   ├── runtime/            # 运行时推理引擎
│   └── world_sim/          # 世界模拟器
├── mcp/                    # MCP 协议服务
│   ├── server.py           # MCP Server (CodeBuddy 接入)
│   └── tools/              # 暴露给 Agent 的工具集
├── sdk/                    # 开发者 SDK
│   ├── python/             # Python SDK
│   └── gdscript/           # GDScript 扩展库
├── examples/               # 示例项目
│   ├── ai_npc_demo/        # AI NPC 示例
│   └── procedural_world/   # AI 程序化世界生成
├── docs/                   # 文档
└── tests/                  # 测试套件
```

---

## 快速开始

### 安装 CLI

```bash
pip install magicai-godot
# 或从源码安装
git clone https://github.com/leisure1994/magicai-godot
cd magicai-godot
pip install -e .
```

### CLI 基本用法

```bash
# 查看帮助
magicai --help

# 创建新的 AI 原生 Godot 项目
magicai new my-game --template ai-rpg

# 构建项目（无头模式）
magicai build --platform windows --headless

# 启动 MCP Server（供 CodeBuddy 等 Agent 接入）
magicai mcp serve --port 3000

# 运行 AI Agent 自动化任务
magicai agent run --task "generate 10 unique NPC behaviors"

# 与 CodeBuddy 深度协同：生成场景
magicai agent scene --prompt "创建一个中世纪市集场景，含5个有个性的NPC"
```

---

## AI 原生节点（GDScript）

```gdscript
# 示例：AI 驱动的 NPC
extends AINode

@export var personality: String = "friendly merchant"
@export var memory_capacity: int = 50

func _ready():
    ai.set_persona(personality)
    ai.enable_memory(memory_capacity)

func _on_player_interact(player):
    var response = await ai.chat(
        context=get_world_context(),
        message=player.last_message
    )
    speak(response)
    ai.remember("Talked to player at " + str(Time.get_time_string_from_system()))
```

---

## CodeBuddy / Agent 集成

### 启动 MCP 服务

```bash
magicai mcp serve
# MCP Server running at http://localhost:3000
# CodeBuddy 中配置: magicai-godot MCP Server
```

### 可用 MCP 工具（供 Agent 调用）

| 工具名 | 描述 |
|--------|------|
| `create_scene` | 根据自然语言描述创建 Godot 场景 |
| `generate_npc` | 生成具有个性的 NPC 节点 |
| `write_gdscript` | 生成 GDScript 代码并写入项目 |
| `run_scene` | 无头运行指定场景并返回日志 |
| `build_project` | 触发构建流水线 |
| `analyze_project` | 分析项目结构并给出 AI 建议 |
| `hotreload` | 热重载指定脚本/场景 |

---

## 路线图

- [x] 项目架构初始化
- [x] CLI 工具链骨架
- [x] MCP Server 框架
- [ ] AI 原生节点库（`AINode`, `AIBehavior`, `AIWorld`）
- [ ] 运行时 LLM 推理引擎（本地 + 云端）
- [ ] CodeBuddy Skill 插件
- [ ] Godot 编辑器插件（AI 面板）
- [ ] 世界模拟器（NPC 社会行为）
- [ ] 多平台构建自动化

---

## 技术栈

- **引擎核心**：Godot 4.x (GDScript / C#)
- **AI 运行时**：Python + LiteLLM（多模型统一接口）
- **CLI**：Python + Click
- **Agent 协议**：MCP (Model Context Protocol)
- **通信**：WebSocket + JSON-RPC

---

## License

MIT © leisure1994
