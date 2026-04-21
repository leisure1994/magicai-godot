## AIController — 封装 LLM 调用与记忆管理
extends Node
class_name AIController

var model: String = "gpt-4o"
var _memory: Array[Dictionary] = []
var _persona: String = ""
var _memory_capacity: int = 20


func set_persona(persona: String) -> void:
	_persona = persona


func enable_memory(capacity: int = 20) -> void:
	_memory_capacity = capacity


func chat(context: Dictionary, message: String) -> String:
	var messages = _build_messages(context, message)
	var response = await _call_llm(messages)
	remember("Q: " + message + " A: " + response)
	return response


func remember(info: String) -> void:
	_memory.append({"info": info, "time": Time.get_unix_time_from_system()})
	if _memory.size() > _memory_capacity:
		_memory.pop_front()


func forget() -> void:
	_memory.clear()


func _build_messages(context: Dictionary, user_message: String) -> Array:
	var system = "You are %s. Context: %s" % [_persona, JSON.stringify(context)]
	if _memory.size() > 0:
		system += " Memory: " + _memory.map(func(m): return m.info).join("; ")
	return [{"role": "system", "content": system}, {"role": "user", "content": user_message}]


func _call_llm(messages: Array) -> String:
	var http = HTTPRequest.new()
	add_child(http)
	http.request("http://127.0.0.1:7788/v1/chat",
		["Content-Type: application/json"], HTTPClient.METHOD_POST,
		JSON.stringify({"model": model, "messages": messages}))
	var result = await http.request_completed
	http.queue_free()
	if result[1] == 200:
		var resp = JSON.parse_string(result[3].get_string_from_utf8())
		return resp.get("content", "...")
	return "[AI 暂时无法响应]"
