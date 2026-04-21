"""
MagicAI Scene Builder - 批量搭建完整 Godot 场景

用法:
  python build_scene.py platformer   # 平台跳跃
  python build_scene.py rpg          # RPG 场景
  python build_scene.py shooter      # 射击游戏
"""
from __future__ import annotations
import json, sys, time
import godot_controller as godot
import ai_script_writer as writer

SCENE_BLUEPRINTS = {
    "platformer": {
        "description": "2D 平台跳跃游戏",
        "nodes": [
            {"name":"World","type":"Node2D"},{"name":"Player","type":"CharacterBody2D"},
            {"name":"Enemies","type":"Node2D"},{"name":"Enemy_01","type":"CharacterBody2D"},
            {"name":"Enemy_02","type":"CharacterBody2D"},{"name":"Platforms","type":"Node2D"},
            {"name":"Ground","type":"StaticBody2D"},{"name":"Platform_01","type":"StaticBody2D"},
            {"name":"Items","type":"Node2D"},{"name":"Coin_01","type":"Area2D"},
            {"name":"UI","type":"CanvasLayer"},{"name":"GameManager","type":"Node"},
        ],
        "scripts": [("player","res://scripts/player.gd"),("enemy","res://scripts/enemy.gd"),("gamemanager","res://scripts/game_manager.gd")]
    },
    "rpg": {
        "description": "RPG 俯视角场景",
        "nodes": [
            {"name":"World","type":"Node2D"},{"name":"Player","type":"CharacterBody2D"},
            {"name":"NPCs","type":"Node2D"},{"name":"Merchant","type":"Node2D"},
            {"name":"Elder","type":"Node2D"},{"name":"Enemies","type":"Node2D"},
            {"name":"Slime_01","type":"CharacterBody2D"},{"name":"Slime_02","type":"CharacterBody2D"},
            {"name":"Items","type":"Node2D"},{"name":"Chest_01","type":"Node2D"},
            {"name":"UI","type":"CanvasLayer"},{"name":"DialogueBox","type":"Control"},
            {"name":"GameManager","type":"Node"},
        ],
        "scripts": [("player","res://scripts/player.gd"),("npc","res://scripts/npc.gd"),("enemy","res://scripts/enemy.gd"),("gamemanager","res://scripts/game_manager.gd")]
    },
    "shooter": {
        "description": "2D 射击游戏",
        "nodes": [
            {"name":"World","type":"Node2D"},{"name":"Player","type":"CharacterBody2D"},
            {"name":"BulletPool","type":"Node2D"},{"name":"Enemies","type":"Node2D"},
            {"name":"Enemy_01","type":"CharacterBody2D"},{"name":"Enemy_02","type":"CharacterBody2D"},
            {"name":"Enemy_03","type":"CharacterBody2D"},{"name":"Obstacles","type":"Node2D"},
            {"name":"Wall_01","type":"StaticBody2D"},{"name":"Cover_01","type":"StaticBody2D"},
            {"name":"UI","type":"CanvasLayer"},{"name":"GameManager","type":"Node"},
        ],
        "scripts": [("player","res://scripts/player.gd"),("enemy","res://scripts/enemy.gd"),("bullet","res://scripts/bullet.gd"),("gamemanager","res://scripts/game_manager.gd")]
    },
}

def build(name: str) -> dict:
    bp = SCENE_BLUEPRINTS.get(name)
    if not bp: return {"ok":False,"error":f"蓝图不存在: {name}，可用: {list(SCENE_BLUEPRINTS.keys())}"}
    print(f"\n{'='*50}\n[SceneBuilder] 构建: {bp['description']}\n{'='*50}")
    node_results = []
    for n in bp["nodes"]:
        r = godot.create_node(n["name"], n["type"])
        print(f"  {'✅' if r.get('ok') else '❌'} {n['type']:20s} → {n['name']}")
        node_results.append(r); time.sleep(0.05)
    script_results = []
    for tmpl, path in bp.get("scripts",[]):
        r = writer.generate_and_write(tmpl, path)
        print(f"  {'✅' if r.get('ok') else '❌'} {tmpl:15s} → {path}")
        script_results.append(r)
    save_r = godot.save_scene()
    ok_n = sum(1 for r in node_results if r.get("ok"))
    ok_s = sum(1 for r in script_results if r.get("ok"))
    print(f"\n完成！节点 {ok_n}/{len(node_results)}  脚本 {ok_s}/{len(script_results)}\n")
    return {"ok":True,"blueprint":name,"nodes_created":ok_n,"scripts_written":ok_s,"saved":save_r.get("ok")}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: python build_scene.py <蓝图>\n可用: {list(SCENE_BLUEPRINTS.keys())}"); sys.exit(0)
    print(json.dumps(build(sys.argv[1]), ensure_ascii=False, indent=2))
