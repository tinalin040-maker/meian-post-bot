# -*- coding: utf-8 -*-
import json
import os
import requests
import io
from PIL import Image
import sys

# 將專案路徑加入 Python Path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from compose_image import upload_to_catbox

json_path = r"c:\ai-agent-center\projects\美安貼文bot\output\2026-07-11.json"

with open(json_path, "r", encoding="utf-8") as f:
    items = json.load(f)

# 定義下載 Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

# 1. 直接定義從 tw.shop.com 與商店抓取到的「原始商品真實照片網址」（已過濾掉 Logo，只保留有吸引力的真實商品照）
img_urls_to_process = [
    [
        "https://img.1shop.tw/vbgLKry7PRnG9qKN1XlEOMV3/1LPZao453vJL07WV3QAR86mM/original-2.jpg.avif",
        "https://img.1shop.tw/vbgLKry7PRnG9qKN1XlEOMV3/v5zx6meKY4vkKVz2l0DVkLyo/original-2.png.avif"
    ],  # OKO
    [
        "https://image-cdn-flare.qdm.cloud/q6f9dba8633ef6/image/data/2026/01/13/a84bd2497ab1569c43d95414e8bfd3c8.png",
        "https://image-cdn-flare.qdm.cloud/q6f9dba8633ef6/image/data/2026/01/12/818cfadeb0b8387c1210e444b1f897f2.jpg"
    ],  # ALARSTAR
    [
        "https://img.shop.com/Image/240000/246200/246292/products/644795621.jpg",
        "https://img.shop.com/Image/240000/246200/246292/skualt/1725298.jpg",
        "https://img.shop.com/Image/240000/246200/246292/skualt/3202892.jpg"
    ]  # Isotonix
]

# 2. 重新規劃精美豐富的 5 行排版文案
oko_desc = (
    "🌱 國際公平貿易認證，友善小農來源透明\n"
    "☕ 嚴選阿拉比卡豆，冷凍乾燥法鎖新鮮香醇\n"
    "✨ 純黑無添加糖和奶精，帶有微蜜糖花香\n"
    "🏨 礁溪老爺酒店客房客用指定款！\n"
    "🥛 也是調製「400次咖啡」的完美首選！"
)

alarstar_desc = (
    "🧴 超柔細泡沫粒子，深層清潔腋下毛孔\n"
    "🌿 不堵塞汗腺，從源頭帶走汗味與異味\n"
    "❌ 無酒精、無香精、無鋁鹽，不殘留皮膚\n"
    "🔬 通過 SGS 重金屬與微生物安心檢測\n"
    "🎁 結帳輸入優惠碼【SU2026】現折 30 元！"
)

isotonix_desc = (
    "💪 綜合消化酵素一次補齊 5 大核心分解酵素\n"
    "🌟 包含澱粉、蛋白、乳糖、纖維與脂肪酵素\n"
    "🦠 芽孢乳酸菌幫助維持消化道機能與菌叢生態\n"
    "🌱 不含麩質、全素可食，不含基改成分\n"
    "✨ 隨身包攜帶超方便，定期購即享 9 折優惠！"
)

descs = [oko_desc, alarstar_desc, isotonix_desc]

for idx, item in enumerate(items):
    # 更新文案
    item["desc"] = descs[idx]
    
    # 下載、轉檔並上傳設定的主圖片 (只取 1 張以防版面擁擠)
    catbox_urls = []
    for img_idx, url in enumerate(img_urls_to_process[idx][:1]):
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            
            # 儲存為臨時的 JPEG
            temp_path = f"C:\\Users\\tinal\\claude-terminal\\temp_prod_{idx}_{img_idx}.jpg"
            img.save(temp_path, "JPEG", quality=90)
            
            # 上傳至 Catbox
            catbox_url = upload_to_catbox(temp_path)
            catbox_urls.append(catbox_url)
            
            # 清理臨時檔案
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            # 若單張圖下載失敗，跳過並記錄
            pass
            
    # 將圖片替換為處理後的 catbox 短網址
    if catbox_urls:
        item["images"] = catbox_urls

    # 6. 安全清理 link 空格
    if "link" in item:
        item["link"] = item["link"].replace(" ", "%20")

# 儲存更新後的 JSON 檔案
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print("JSON file updated successfully with original image URLs.")
