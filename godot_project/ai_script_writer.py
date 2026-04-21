"""
MagicAI Script Writer - AI 生成 GDScript 并写入 Godot

用法:
  python ai_script_writer.py player
  python ai_script_writer.py enemy  res://scripts/boss.gd
  python ai_script_writer.py npc
  python ai_script_writer.py gamemanager
  python ai_script_writer.py bullet
"""
from __future__ import annotations
import os, sys, json
import godot_controller as godot

TEMPLATES: dict[str, tuple[str, str]] = {
    "player": ("res://scripts/player.gd", 'extends CharacterBody2D\n\nconst SPEED = 200.0\nconst JUMP_VELOCITY = -400.0\n\nfunc _physics_process(delta: float) -> void:\n\tif not is_on_floor():\n\t\tvelocity += get_gravity() * delta\n\tif Input.is_action_just_pressed("ui_accept") and is_on_floor():\n\t\tvelocity.y = JUMP_VELOCITY\n\tvar direction = Input.get_axis("ui_left", "ui_right")\n\tif direction:\n\t\tvelocity.x = direction * SPEED\n\telse:\n\t\tvelocity.x = move_toward(velocity.x, 0, SPEED)\n\tmove_and_slide()\n'),
    "enemy":  ("res://scripts/enemy.gd",  'extends CharacterBody2D\n\n@export var speed: float = 80.0\n@export var patrol_range: float = 100.0\n@export var health: int = 3\nvar direction: float = 1.0\nvar start_x: float = 0.0\n\nfunc _ready() -> void:\n\tstart_x = global_position.x\n\nfunc _physics_process(delta: float) -> void:\n\tif not is_on_floor():\n\t\tvelocity += get_gravity() * delta\n\tvelocity.x = direction * speed\n\tif abs(global_position.x - start_x) >= patrol_range:\n\t\tdirection *= -1.0\n\tmove_and_slide()\n\nfunc take_damage(amount: int) -> void:\n\thealth -= amount\n\tif health <= 0: queue_free()\n'),
    "npc":    ("res://scripts/npc.gd",    'extends Node2D\n\n@export var npc_name: String = "NPC"\n@export var dialogues: Array[String] = ["你好，旅行者！","祝你旅途顺利！"]\nvar dialogue_index: int = 0\n\nfunc interact() -> void:\n\tif dialogue_index < dialogues.size():\n\t\tprint(npc_name + ": " + dialogues[dialogue_index])\n\t\tdialogue_index += 1\n\telse:\n\t\tdialogue_index = 0\n'),
    "gamemanager": ("res://scripts/game_manager.gd", 'extends Node\n\nsignal score_changed(new_score: int)\nsignal game_over\n\nvar score: int = 0\nvar lives: int = 3\n\nfunc add_score(points: int) -> void:\n\tscore += points\n\tscore_changed.emit(score)\n\nfunc lose_life() -> void:\n\tlives -= 1\n\tif lives <= 0: game_over.emit()\n\nfunc restart() -> void:\n\tscore = 0; lives = 3\n\tget_tree().reload_current_scene()\n'),
    "bullet": ("res://scripts/bullet.gd", 'extends Area2D\n\n@export var speed: float = 400.0\n@export var damage: int = 1\nvar direction: Vector2 = Vector2.RIGHT\n\nfunc _ready() -> void:\n\tget_tree().create_timer(2.0).timeout.connect(queue_free)\n\nfunc _physics_process(delta: float) -> void:\n\tposition += direction * speed * delta\n\nfunc _on_body_entered(body: Node2D) -> void:\n\tif body.has_method("take_damage"): body.take_damage(damage)\n\tqueue_free()\n'),
}

def generate_and_write(description: str, target_path: str | None = None) -> dict:
    key = description.lower().strip()
    if key in TEMPLATES:
        path, code = TEMPLATES[key]
        if target_path: path = target_path
        print(f"[ScriptWriter] 模板: {key} → {path}")
        r = godot.write_script(path, code)
        r["code_preview"] = code[:100] + "..."
        return r
    code = _llm_generate(description)
    if code is None:
        return {"ok": False, "error": f"LLM 不可用。可用模板: {list(TEMPLATES.keys())}"}
    path = target_path or f"res://scripts/{key.replace(' ','_')}.gd"
    r = godot.write_script(path, code)
    r["code_preview"] = code[:100] + "..."
    return r

def _llm_generate(desc: str) -> str | None:
    try:
        import litellm
        resp = litellm.completion(model=os.environ.get("MAGICAI_MODEL","gpt-4o"),
            messages=[{"role":"user","content":f"用 Godot 4 GDScript 实现: {desc}，只输出代码"}], temperature=0.3)
        code = resp.choices[0].message.content.strip()
        if code.startswith("```"):
            lines = code.split("\n"); code = "\n".join(lines[1:-1])
        return code
    except Exception as e:
        print(f"[ScriptWriter] LLM 失败: {e}"); return None

def list_templates(): return list(TEMPLATES.keys())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"用法: python ai_script_writer.py <模板名>\n可用: {list_templates()}"); sys.exit(0)
    r = generate_and_write(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else None)
    print(json.dumps(r, ensure_ascii=False, indent=2))
