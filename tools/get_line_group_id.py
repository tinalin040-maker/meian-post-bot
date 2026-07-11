"""
一次性小工具：接收 LINE webhook 事件，印出 Bot 被加入群組時的 Group ID。
用法：搭配 ngrok 暴露本機 port，設定成 LINE Developers Console 的 Webhook URL。
設定完成、拿到 Group ID 後即可關閉，不需要長期運行。
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8787


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.send_response(200)
        self.end_headers()

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return

        for event in payload.get("events", []):
            source = event.get("source", {})
            if source.get("type") == "group":
                group_id = source.get("groupId")
                print(f"[取得 Group ID] {group_id}")
            else:
                print(f"[收到事件] type={event.get('type')} source={source}")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    print(f"監聽中 http://localhost:{PORT}/webhook ...（把 Bot 加入群組後這裡會印出 Group ID）")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
