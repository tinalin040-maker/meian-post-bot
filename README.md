# 美安商品貼文自動化 Bot (meian-post-bot)

本專案為 **美安商品貼文自動化系統**，旨在每天自動抓取並精選美安商品（包含夥伴商店商品與獨家品牌商品），進行格式與連結的嚴格自我校驗，然後透過 LINE LIFF 機制產生滿版的 Flex Card 分享卡片發送至群組，並同步紀錄至 Google Sheets。

---

## 🌟 核心特色與自動校驗機制

本系統具備「**零出錯自動防呆機制**」，程式在每天晚上 19:45 執行時，會自動進行以下三關卡自我檢測：

1. **金額格式與邏輯自動檢查**：
   * 使用正則表達式（Regex）驗證金額是否符合 `NT$數字` 格式（如 `NT$1,299`），若出現空值或損毀（如只有 `NT`）即刻中斷。
   * **價格邏輯比對**：驗證「原價大於或等於特價」，防止原價低於特價的排版邏輯錯誤。若不符，程式會自動捨棄該商品，重新挑選下一款商品。
2. **連結有效性自動檢測**：
   * 系統會自動對商品 URL 進行背景 HTTP 連線檢驗，確保回傳狀態碼為 `200`（正常網頁）。
   * 檢查網址是否包含美安的官方商品實體 ID（如 `-1984990700-p+.xhtml`），防止無效的 404 或被封鎖網頁被發送。若檢測失敗，會自動切換其他商品。
3. **排版格式檢測**：
   * 自動校驗商品介紹文案是否符合 **5 行** 行數限制，並檢查卡片底部的「馬上私訊 Ethan我」與「* 未達免運，需付運費」小字是否完整呈現。

---

## 🛠️ 專案技術棧

* **語言與庫**：Python 3.10+, Playwright (用於背景抓取與驗證)
* **資料紀錄**：Google Sheets API (gspread)
* **訊息推播**：LINE Messaging API + LINE LIFF (實現群組免費卡片分享，不扣除官方推播額度)
* **縮網址服務**：TinyURL API
* **圖片託管**：Catbox.moe API (用於轉換並託管高畫質 JPEG 商品照)

---

## 📂 資料夾結構

```text
美安貼文bot/
├── liff/                # LIFF 網頁代碼 (託管於 GitHub Pages)
│   └── index.html       # 滿版 Flex 卡片預覽與一鍵分享頁面
├── skills/              # AI 助理的 Skills 指令檔
│   └── daily_post.md    # 每日貼文流程的 AI 規範
├── tools/               # 核心執行腳本
│   ├── send_line_message.py  # LINE 卡片封裝與 TinyURL 短網址發送
│   └── write_to_sheets.py    # Google Sheets 資料同步紀錄工具
├── output/              # 每日抓取的商品 JSON 暫存檔
├── requirements.txt     # Python 依賴庫
├── run_daily_post.ps1   # Windows 排程啟動腳本
├── PROJECT.md           # 專案技術細節與備忘錄
└── README.md            # 本說明文件
```

---

## ⚙️ 環境設定與部署

### 1. 安裝依賴環境
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. 環境變數設定 (`.env`)
請在專案根目錄下建立 `.env` 檔案並填入以下內容：
```ini
# LINE 設定
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_GROUP_ID=your_line_group_id  # 小群組 (2-shop) 的 ID

# LIFF 設定
LIFF_ID=your_liff_id              # LINE LIFF App ID
LIFF_URL=https://your-github-username.github.io/meian-liff-share-helper/

# Google Sheets 設定
SPREADSHEET_NAME=美安商品貼文紀錄
```

### 3. Google 服務帳號金鑰
請將 Google Cloud 服務帳號的憑證 JSON 檔案儲存於 `credentials/service_account.json`（已在 `.gitignore` 中設定忽略防洩漏）。

---

## 📅 每日排程運作方式

系統已設定 Windows 工作排程器（Task Scheduler），於 **每天晚上 19:45** 執行以下流程：
1. 執行 `run_daily_post.ps1`。
2. 背景啟動 Playwright 爬蟲，進行 3 組全新商品的尋找與抓取。
3. 執行 **自動自我校驗機制**（金額、連結與排版格式）。
4. 自動下載圖片、上傳至 Catbox，生成 `output/<今天日期>.json`。
5. 執行 `tools/send_line_message.py`：
   * 將 JSON 資料進行 Base64 編碼，封裝進 LIFF URL 中。
   * 將 LIFF URL 轉換為 TinyURL 短網址。
   * 推送短網址訊息至 LINE 小群組（2-shop）。
   * 調用 `tools/write_to_sheets.py` 將正確的品名、原價、特價及原始網址同步記錄至 Google Sheets。
