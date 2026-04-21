@tool
## AINode — MagicAI 引擎 AI 原生基础节点
## 所有 AI 驱动节点的基类，内置 LLM 推理、记忆、上下文感知能力
extends Node
class_name AINode

var ai: AIController

@export var ai_enabled: bool = true
@export var model_override: String = ""

signal spoke(text: String)


func _ready() -> void:
	ai = AIController.new()
	ai.model = model_override if model_override != "" else MagicAI.default_model
	add_child(ai)
	if ai_enabled:
		_on_ai_ready()


func _on_ai_ready() -> void:
	pass


func get_world_context() -> Dictionary:
	return {
		"node_name": name,
		"scene": get_tree().current_scene.name if get_tree() else "unknown",
		"time": Time.get_time_string_from_system(),
	}


func speak(text: String) -> void:
	print("[%s] %s" % [name, text])
	emit_signal("spoke", text)
