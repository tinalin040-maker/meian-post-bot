# -*- coding: utf-8 -*-
import os
import sys
import requests
from dotenv import load_dotenv

# 取得專案根目錄
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_dir, ".env"))

token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
group_id = os.getenv("LINE_GROUP_ID")

if not token or not group_id:
    print("錯誤：.env 中未設定 LINE_CHANNEL_ACCESS_TOKEN 或 LINE_GROUP_ID")
    sys.exit(1)

# 取得錯誤訊息參數
err_msg = sys.argv[1] if len(sys.argv) > 1 else "貼文機器人執行異常！"

url = "https://api.line.me/v2/bot/message/push"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
payload = {
    "to": group_id,
    "messages": [
        {
            "type": "text",
            "text": f"⚠️ 貼文機器人警報：\n\n{err_msg}"
        }
    ]
}

try:
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    if resp.status_code == 200:
        print("警報已成功送出至 LINE！")
    else:
        print(f"發送警報失敗，狀態碼：{resp.status_code}，回應：{resp.text}")
except Exception as e:
    print("連線 LINE API 時發生異常：", e)
