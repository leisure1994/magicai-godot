@tool
extends EditorPlugin

var server: TCPServer
var clients: Array = []
const PORT = 8765

func _enter_tree() -> void:
	server = TCPServer.new()
	var err = server.listen(PORT)
	if err == OK:
		print("[MagicAI] ✅ 编辑器控制服务启动，端口: ", PORT)
	else:
		print("[MagicAI] ❌ 端口监听失败，错误码: ", err)

func _process(_delta: float) -> void:
	while server and server.is_connection_available():
		var c = server.take_connection()
		clients.append(c)
		print("[MagicAI] 新连接来自 AI Agent")
	for c in clients.duplicate():
		if c.get_status() != StreamPeerTCP.STATUS_CONNECTED:
			clients.erase(c); continue
		var available = c.get_available_bytes()
		if available > 0:
			var raw_bytes = c.get_data(available)
			var raw = raw_bytes[1].get_string_from_utf8()
			var cmd = JSON.parse_string(raw)
			if cmd:
				var result = _handle_command(cmd)
				c.put_data((JSON.stringify(result) + "\n").to_utf8_buffer())

func _handle_command(cmd: Dictionary) -> Dictionary:
	var action = cmd.get("action", "")
	print("[MagicAI] 指令: ", action)
	match action:
		"ping":
			return {"ok": true, "message": "pong", "godot_version": str(Engine.get_version_info()["string"])}
		"create_node":
			var scene = get_editor_interface().get_edited_scene_root()
			if not scene: return {"ok": false, "error": "没有打开的场景"}
			var type = cmd.get("type", "Node")
			var node: Node
			match type:
				"Node2D":          node = Node2D.new()
				"Node3D":          node = Node3D.new()
				"Label":           node = Label.new()
				"Sprite2D":        node = Sprite2D.new()
				"CharacterBody2D": node = CharacterBody2D.new()
				"StaticBody2D":    node = StaticBody2D.new()
				"Area2D":          node = Area2D.new()
				"CanvasLayer":     node = CanvasLayer.new()
				"Control":         node = Control.new()
				_:                 node = Node.new()
			node.name = cmd.get("name", "AINode")
			scene.add_child(node); node.owner = scene
			return {"ok": true, "message": "节点已创建: " + node.name, "type": type}
		"delete_node":
			var scene = get_editor_interface().get_edited_scene_root()
			if not scene: return {"ok": false, "error": "没有打开的场景"}
			var target = scene.find_child(cmd.get("name",""), true, false)
			if target: target.queue_free(); return {"ok": true, "message": "已删除: " + cmd.get("name","")}
			return {"ok": false, "error": "找不到节点: " + cmd.get("name","")}
		"set_property":
			var scene = get_editor_interface().get_edited_scene_root()
			if not scene: return {"ok": false, "error": "没有打开的场景"}
			var target = scene.find_child(cmd.get("node",""), true, false)
			if not target: return {"ok": false, "error": "找不到节点"}
			target.set(cmd.get("property",""), cmd.get("value"))
			return {"ok": true, "message": "属性已设置"}
		"play":
			get_editor_interface().play_main_scene()
			return {"ok": true, "message": "场景已启动"}
		"stop":
			get_editor_interface().stop_playing_scene()
			return {"ok": true, "message": "场景已停止"}
		"save_scene":
			get_editor_interface().save_scene()
			return {"ok": true, "message": "场景已保存"}
		"open_scene":
			get_editor_interface().open_scene_from_path(cmd.get("path",""))
			return {"ok": true, "message": "已打开: " + cmd.get("path","")}
		"list_nodes":
			var scene = get_editor_interface().get_edited_scene_root()
			if not scene: return {"ok": false, "error": "没有打开的场景"}
			var nodes = []; _collect_nodes(scene, nodes)
			return {"ok": true, "nodes": nodes}
		"write_script":
			var path = cmd.get("path", "")
			var code = cmd.get("code", "")
			if path == "" or code == "": return {"ok": false, "error": "path 和 code 不能为空"}
			var real_path = path
			if path.begins_with("res://"):
				real_path = ProjectSettings.globalize_path(path)
			DirAccess.make_dir_recursive_absolute(real_path.get_base_dir())
			var file = FileAccess.open(real_path, FileAccess.WRITE)
			if not file: return {"ok": false, "error": "无法写入: " + real_path}
			file.store_string(code); file.close()
			return {"ok": true, "message": "脚本已写入: " + real_path}
		_:
			return {"ok": false, "error": "未知指令: " + action}

func _collect_nodes(node: Node, result: Array) -> void:
	result.append({"name": node.name, "type": node.get_class()})
	for child in node.get_children(): _collect_nodes(child, result)

func _exit_tree() -> void:
	if server: server.stop()
	print("[MagicAI] 编辑器控制服务已关闭")
