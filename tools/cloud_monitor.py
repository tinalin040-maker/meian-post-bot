# -*- coding: utf-8 -*-
import os
import sys
import json
from datetime import datetime
import pytz
import gspread
import requests

# 從 GitHub Secrets 載入環境變數
service_account_json_str = os.getenv("SERVICE_ACCOUNT_JSON")
token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
group_id = os.getenv("LINE_GROUP_ID")

if not service_account_json_str or not token or not group_id:
    print("錯誤：缺少必要的環境變數 (SERVICE_ACCOUNT_JSON, LINE_CHANNEL_ACCESS_TOKEN, LINE_GROUP_ID)")
    sys.exit(1)

# 連線 Google Sheets
try:
    info = json.loads(service_account_json_str)
    gc = gspread.service_account_from_dict(info)
    sh = gc.open("美安商品貼文紀錄")
    ws = sh.get_worksheet(0)
except Exception as e:
    print("連線 Google Sheets 失敗：", e)
    sys.exit(1)

# 取得台灣時區的今天日期
tz_tw = pytz.timezone("Asia/Taipei")
today_str = datetime.now(tz_tw).strftime("%Y-%m-%d")
print(f"正在檢查試算表中是否有今日日期：{today_str} ...")

# 檢查第一欄（日期欄）
try:
    dates = ws.col_values(1)
    has_today = today_str in dates
except Exception as e:
    print("讀取試算表資料失敗：", e)
    sys.exit(1)

if not has_today:
    print(f"【警報】試算表中未找到今日日期 {today_str} 的紀錄！正發送 LINE 警告...")
    
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
                "text": f"⚠️ 貼文機器人雲端警報：\n\n偵測到今日 ({today_str}) 的 Google Sheets 尚無任何貼文商品紀錄！\n\n這代表您家中的電腦此時可能未開機、或是當機未順利執行。請確認電腦狀態，並手動進行補發貼文。"
            }
        ]
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            print("雲端監控警報已成功送出至 LINE！")
        else:
            print(f"雲端監控警報發送失敗，狀態碼：{resp.status_code}，回應：{resp.text}")
    except Exception as e:
        print("連線 LINE API 時發生異常：", e)
else:
    print(f"【正常】已在試算表中找到今日日期 {today_str} 的紀錄。無須警報。")
