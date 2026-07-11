"""
把每日商品貼文資料編碼為 LIFF 連結，並發送文字通知到「2-shop」群組。
使用者點選連結後，會開起 LIFF 網頁，一鍵將「滿版 Flex 卡片」分享至大群組，完全不消耗官方帳號額度。

用法：
    python tools/send_line_message.py <items.json>

憑證與設定從環境變數讀取：
    LINE_CHANNEL_ACCESS_TOKEN
    LINE_GROUP_ID
    LINE_LIFF_ID
"""

import base64
import io
import json
import os
import sys
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

load_dotenv()

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


def build_liff_url(items: list[dict]) -> str:
    liff_id = os.environ.get("LINE_LIFF_ID", "YOUR_LIFF_ID_HERE")
    
    # 縮寫欄位以節省網址長度
    shortened = []
    for item in items:
        s_item = {
            "n": item.get("name", ""),
            "ps": item.get("price_sale", ""),
        }
        if item.get("price_original"):
            s_item["po"] = item["price_original"]
        if item.get("desc"):
            # 限制描述在 150 字內以防網址過長，並保留換行以利分行排版
            desc_val = item["desc"].strip()
            if len(desc_val) > 150:
                s_item["d"] = desc_val[:150] + "..."
            else:
                s_item["d"] = desc_val
        if item.get("images"):
            # 只放 1 張主圖以防版面擁擠且版面更好看
            s_item["i"] = item["images"][:1]
        # 不加入連結 (l) 欄位，因為卡片詳情按鈕已被移除，省去大量 URL 空間
        shortened.append(s_item)

    # 轉為 JSON 後進行 Base64 UTF-8 編碼
    json_data = json.dumps(shortened, ensure_ascii=False)
    encoded_bytes = base64.urlsafe_b64encode(json_data.encode("utf-8"))
    encoded_str = encoded_bytes.decode("utf-8")

    # 組合連結，同時在 query 傳入 liffId 以便 LIFF 網頁自動讀取免寫死
    long_url = f"https://liff.line.me/{liff_id}?data={encoded_str}&liffId={liff_id}"
    return shorten_url(long_url)


def shorten_url(long_url: str) -> str:
    try:
        import urllib.parse
        encoded_url = urllib.parse.quote(long_url)
        resp = requests.get(f"https://tinyurl.com/api-create.php?url={encoded_url}", timeout=10)
        if resp.status_code == 200:
            short_url = resp.text.strip()
            if short_url.startswith("http"):
                return short_url
    except Exception as e:
        print(f"URL 縮短失敗: {e}", file=sys.stderr)
    return long_url


def send(items: list[dict]) -> None:
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    group_id = os.environ["LINE_GROUP_ID"]
    
    liff_url = build_liff_url(items)

    message_text = (
        "【今日精選美安商品】\n"
        "已為您自動生成今日商品的滿版分享卡片！\n"
        "請點擊以下連結，一鍵分享至您的大群組（不消耗官方帳號點數）：\n\n"
        f"🔗 分享連結：\n{liff_url}\n\n"
        "（說明：點開連結後點擊「分享到群組」，選擇您的 80 人群組發送即可）"
    )

    messages = [
        {
            "type": "text",
            "text": message_text
        }
    ]

    resp = requests.post(
        LINE_PUSH_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"to": group_id, "messages": messages},
        timeout=15,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"LINE push 失敗: {resp.status_code} {resp.text}")

    print(f"2-shop 群組 LIFF 連結發送成功！共包裝了 {len(items)} 樣商品。\n分享連結為: {liff_url}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python tools/send_line_message.py <items.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        items = json.load(f)

    try:
        send(items)
        # 自動執行 write_to_sheets.py 寫入 Google Sheets 紀錄
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sheets_script = os.path.join(script_dir, "write_to_sheets.py")
        if os.path.exists(sheets_script):
            print("正在自動同步紀錄至 Google Sheets...")
            import subprocess
            subprocess.run([sys.executable, sheets_script], check=False)
    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)
