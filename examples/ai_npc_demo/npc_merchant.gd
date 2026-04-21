## 示例：AI 驱动的商人 NPC
extends AINode

@export var shop_items: Array[String] = ["剑", "盾", "药水", "地图"]


func _on_ai_ready() -> void:
	ai.set_persona("你是精明热情的中世纪商人 Baldric，卖武器和药品。")
	ai.enable_memory(30)


func _on_player_interact(player_node) -> void:
	var ctx = get_world_context()
	ctx["shop_items"] = shop_items
	ctx["player_gold"] = player_node.get("gold", 0)
	var greeting = await ai.chat(context=ctx,
		message="玩家走近了你的摊位。请热情打招呼并介绍商品。")
	speak(greeting)


func sell_item(item: String, _player_node) -> void:
	var response = await ai.chat(context=get_world_context(),
		message="玩家想买: " + item)
	speak(response)
	ai.remember("卖出了 " + item)
