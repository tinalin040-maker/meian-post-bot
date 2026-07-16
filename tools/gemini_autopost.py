# -*- coding: utf-8 -*-
"""
使用免費 Google Gemini API 實現全自動的美安商品貼文自動化。
會讀取專案 skills/daily_post.md 的選品與文案規範，
使用 Playwright 以 headed 模式抓取 tw.shop.com 促銷頁面資訊，
經由 Gemini 智慧選品並自動完成圖片 Litterbox/Catbox 上傳、Sheets 紀錄與 LINE 發送。
"""

import os
import re
import json
import sys
import glob
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import requests

# 將本目錄加入路徑以方便導入 compose_image
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compose_image import upload_to_catbox

# 強制控制台輸出為 UTF-8
import io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

load_dotenv()

# 設定 Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("【錯誤】未偵測到 GEMINI_API_KEY 環境變數！")
    print("請在 .env 檔案中填入: GEMINI_API_KEY=您的金鑰")
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    print("未安裝 google-generativeai 套件。正在嘗試安裝...")
    subprocess.run([sys.executable, "-m", "pip", "install", "google-generativeai"], check=True)
    import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)


def get_shop_data_with_playwright():
    """使用 Playwright 以 headed 模式抓取促銷頁面資訊，防 Cloudflare 挑戰"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("未安裝 playwright 套件。正在嘗試安裝...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        subprocess.run(["playwright", "install", "chromium"], check=True)
        from playwright.sync_api import sync_playwright

    print("正在啟動瀏覽器抓取商品資訊...")
    hot_url = "https://tw.shop.com/hot-deals"
    daily_url = "https://tw.shop.com/daily-deals"
    
    hot_data = ""
    daily_data = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 必須 headed 避開 CF 挑戰
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        try:
            # 1. 抓取 hot-deals
            print(f"前往 {hot_url} ...")
            page.goto(hot_url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)
            
            # 提取 links 與 text
            links = page.evaluate("""() => {
                const res = [];
                document.querySelectorAll('a').forEach(a => {
                    const text = a.innerText ? a.innerText.trim() : '';
                    if (text.length > 2 && a.href && a.href.startsWith('http')) {
                        res.push(`${text} | URL: ${a.href}`);
                    }
                });
                return res;
            }""")
            
            body_text = page.locator("body").inner_text()
            hot_data = "=== LINKS ===\n" + "\n".join(links) + "\n\n=== TEXT ===\n" + body_text
            
            # 2. 抓取 daily-deals
            print(f"前往 {daily_url} ...")
            page.goto(daily_url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)
            
            links_daily = page.evaluate("""() => {
                const res = [];
                document.querySelectorAll('a').forEach(a => {
                    const text = a.innerText ? a.innerText.trim() : '';
                    if (text.length > 2 && a.href && a.href.startsWith('http')) {
                        res.push(`${text} | URL: ${a.href}`);
                    }
                });
                return res;
            }""")
            
            body_text_daily = page.locator("body").inner_text()
            daily_data = "=== LINKS ===\n" + "\n".join(links_daily) + "\n\n=== TEXT ===\n" + body_text_daily
            
        except Exception as e:
            print(f"網頁抓取過程中發生錯誤: {e}")
        finally:
            browser.close()
            
    return hot_data, daily_data


def select_and_generate_copy(hot_text: str, daily_text: str) -> list[dict]:
    """呼叫 Gemini 進行商品挑選與行銷文案撰寫"""
    print("正在請求 Gemini 模型進行選品與行銷文案生成...")
    
    # 讀取近幾天的歷史商品紀錄，避免重複
    history_names = []
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_files = glob.glob(os.path.join(project_dir, "output", "*.json"))
    for file in log_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                history_data = json.load(f)
                for item in history_data:
                    history_names.append(item.get("name", ""))
        except Exception:
            pass

    history_context = ""
    if history_names:
        history_context = "【最近已推播過的商品（請絕對不要重複選擇這些商品或品牌，至少避開近7天內的商品）：】\n" + "\n".join(history_names[:21])

    # 讀取母專案的選品規則檔
    rules_path = os.path.join(project_dir, "skills", "daily_post.md")
    rules_content = ""
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            rules_content = f.read()
    else:
        print("警告：未找到 skills/daily_post.md 規則檔。使用內建預設規則。")
        rules_content = "規則：商品一為食品促銷；商品二為非食品促銷；商品三為獨家代理品牌商品。文案為5行格式。"

    prompt = f"""
你是一個精通電子商務與社群行銷的專業小編。下面提供兩個網頁的爬取內容與連結：
1. 熱門促銷頁面 (Hot Deals)
2. 每日一物頁面 (Daily Deals)

請依據以下【選品與貼文規則】完成任務：

【選品與貼文規則內容】：
{rules_content}

{history_context}

請注意：
1. 挑選 3 個符合規則的促銷商品。
2. 針對價格，請仔細比對網頁文字中的原價與特價，確保 100% 正確性，千萬不要捏造或猜測價格。如果網頁沒有明確價格，請由 HTML 當中尋找對應金額，若真的沒有，原價可留空。
3. 文案請嚴格撰寫成 5 行格式，行與行之間以 \\n 字元相隔。
4. 針對 images 欄位，請從 LINKS 或網頁中尋找該商品或店家的原始圖片 URL。例如，如果品牌是「楓格蛋糕」，且其圖片網址格式為 https://img.shop.com/Image/280000/284700/284736/products/XXXXXX.jpg，請將 XXXXXX.jpg 替換為該店的泡芙或其他商品的對應正確 ID！

請嚴格以 JSON 陣列格式輸出，不要包含任何 markdown 語法外框 (如 ```json)。
欄位名稱必須完全一致：
[
  {{
    "name": "商品名稱",
    "price_original": "原價，例如 NT$1,450 (無原價則填空字串)",
    "price_sale": "限時特價，例如 NT$1,305",
    "desc": "您撰寫的 5 行行銷文案 (行與行之間請以 \\n 換行字元相隔)",
    "images": ["商品圖片網址"],
    "url": "商品在 shop.com 的原始購買網址"
  }}
]

---
以下為【1. 熱門促銷頁爬取內容】：
{hot_text[:40000]}

---
以下為【2. 每日一物頁爬取內容】：
{daily_text[:20000]}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        data = json.loads(text)
        return data
    except Exception as e:
        print("Gemini 返回的 JSON 格式解析失敗！原始回應內容如下：")
        print(text)
        raise e


def process_images_and_upload(items: list) -> list:
    """下載商品主圖並上傳至 Catbox/Litterbox 防止 Cloudflare 破圖"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    print("\n正在下載商品主圖並上傳至 Catbox/Litterbox...")
    for idx, item in enumerate(items):
        imgs = item.get("images", [])
        if not imgs:
            continue
            
        raw_img_url = imgs[0]
        # 去除 url 參數以便下載
        download_url = raw_img_url.split("?")[0]
        
        print(f"處理商品 {idx+1} 的圖片: {download_url} ...")
        try:
            resp = requests.get(download_url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            # 存成臨時檔
            temp_path = f"C:\\Users\\tinal\\temp_gemini_prod_{idx}.jpg"
            with open(temp_path, "wb") as temp_f:
                temp_f.write(resp.content)
                
            # 上傳
            public_url = upload_to_catbox(temp_path)
            print(f"上傳成功! 公網 URL: {public_url}")
            
            # 替換為上傳後的 URL
            item["images"] = [public_url]
            
            # 刪除臨時檔
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"商品 {idx+1} 圖片處理失敗: {e}，保留原始連結。")
            item["images"] = [raw_img_url]
            
    return items


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. 抓取網頁資料
    hot_text, daily_text = get_shop_data_with_playwright()

    if not hot_text or not daily_text:
        print("【錯誤】無法順利抓取網頁，終止執行。")
        sys.exit(1)

    # 2. 呼叫 Gemini 進行智慧選品與文案生成
    try:
        items = select_and_generate_copy(hot_text, daily_text)
    except Exception:
        sys.exit(1)

    # 3. 處理圖片下載與上傳
    items = process_images_and_upload(items)

    # 4. 寫入本日 JSON
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(output_dir, f"{today_str}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 成功挑選並生成文案，已寫入本地存檔: {output_path}")

    # 5. 呼叫推播發送腳本 (send_line_message.py)
    send_script = os.path.join(project_dir, "tools", "send_line_message.py")
    if os.path.exists(send_script):
        print("\n正在呼叫推播腳本發送 LINE 卡片與同步 Sheets...")
        # 由於 python path 可能有虛擬環境問題，使用絕對路徑與 python 可執行檔呼叫
        subprocess.run([sys.executable, send_script, output_path], check=True)


if __name__ == "__main__":
    main()
