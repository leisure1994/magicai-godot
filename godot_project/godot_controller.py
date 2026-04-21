"""
MagicAI Godot 控制器
用 Python 直接发指令给 Godot 编辑器
"""
import socket
import json
import sys

GODOT_HOST = "127.0.0.1"
GODOT_PORT = 8765


def send(action: str, **kwargs) -> dict:
    """发送指令到 Godot 编辑器插件"""
    cmd = {"action": action, **kwargs}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((GODOT_HOST, GODOT_PORT))
        s.sendall(json.dumps(cmd).encode("utf-8"))
        s.settimeout(5)
        response = b""
        while b"\n" not in response:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        s.close()
        return json.loads(response.decode("utf-8").strip())
    except ConnectionRefusedError:
        return {"ok": False, "error": "无法连接 Godot，请确认编辑器已启动且插件已启用"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def ping():                              return send("ping")
def create_node(name, node_type="Node"): return send("create_node", name=name, type=node_type)
def delete_node(name):                   return send("delete_node", name=name)
def set_property(node, prop, value):     return send("set_property", node=node, property=prop, value=value)
def play():                              return send("play")
def stop():                              return send("stop")
def save_scene():                        return send("save_scene")
def list_nodes():                        return send("list_nodes")
def write_script(path, code):            return send("write_script", path=path, code=code)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python godot_controller.py <指令> [参数]")
        print("  ping | play | stop | save | list")
        print("  create <name> <type>   例: create Player Node2D")
        print("  delete <name>")
        sys.exit(0)

    cmd = sys.argv[1]
    result = {}
    match cmd:
        case "ping":   result = ping()
        case "play":   result = play()
        case "stop":   result = stop()
        case "save":   result = save_scene()
        case "list":   result = list_nodes()
        case "create":
            name  = sys.argv[2] if len(sys.argv) > 2 else "AINode"
            ntype = sys.argv[3] if len(sys.argv) > 3 else "Node"
            result = create_node(name, ntype)
        case "delete":
            result = delete_node(sys.argv[2])
        case _:
            result = {"ok": False, "error": f"未知指令: {cmd}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))
