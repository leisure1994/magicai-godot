extends SceneTree

func _init():
	print("=== MagicAI CLI 控制成功 ===")
	print("Godot 版本: ", Engine.get_version_info())
	print("当前时间: ", Time.get_datetime_string_from_system())
	quit()
