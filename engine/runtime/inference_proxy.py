"""
MagicAI 推理代理

运行在本地的轻量 HTTP 服务，作为 Godot（GDScript HTTPRequest）
与 LLM 后端（OpenAI / 本地模型）之间的桥梁。
"""

from __future__ import annotations
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

DEFAULT_MODEL = os.environ.get("MAGICAI_MODEL", "gpt-4o")
DEFAULT_PORT = int(os.environ.get("MAGICAI_PROXY_PORT", 7788))


class InferenceHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        result = self._handle_chat(body) if self.path.rstrip("/") == "/v1/chat" \
            else {"error": f"Unknown path: {self.path}"}
        resp = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(resp))
        self.end_headers()
        self.wfile.write(resp)

    def _handle_chat(self, body: dict) -> dict:
        try:
            import litellm
            response = litellm.completion(
                model=body.get("model", DEFAULT_MODEL),
                messages=body.get("messages", []),
            )
            return {"content": response.choices[0].message.content, "model": response.model}
        except ImportError:
            return {"content": "[litellm 未安装，pip install litellm]", "model": "mock"}
        except Exception as e:
            return {"content": f"[推理错误: {e}]", "model": "error"}

    def log_message(self, fmt, *args):
        print(f"[InferenceProxy] {fmt % args}")


def start(port: int = DEFAULT_PORT):
    print(f"[MagicAI InferenceProxy] http://127.0.0.1:{port}")
    HTTPServer(("127.0.0.1", port), InferenceHandler).serve_forever()


if __name__ == "__main__":
    start()
