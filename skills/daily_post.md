# 每日貼文流程（daily_post）

執行時機：每天 19:45，由 Windows 工作排程器觸發 `claude -p`（見 `run_daily_post.ps1`）。
目的：選出 **3 樣商品**（2 樣夥伴商店划算商品：1 食品 + 1 非食品，1 樣獨家品牌商品）。

**使用 LINE LIFF 一鍵分享方案**：
為了兼顧「滿版精美 Flex 卡片效果」與「完全免費不扣除官方帳號推播額度」，本專案採用 LINE LIFF 分享方案。
1. Bot 透過 Messaging API 推送一個包含 LIFF 分享連結的文字訊息至小群組「2-shop」 (`LINE_GROUP_ID`)。
2. 使用者點擊連結後，會在 LINE 中開啟 LIFF 網頁，點選「分享到群組」，即可將 3 樣商品的滿版 Flex 卡片一次分享至 80 人大群組（0 扣點）。

---

## 前置需求

- 這台電腦的 Chrome 瀏覽器必須已開啟，且已用購物顧問帳號登入 tw.shop.com，並登入 Google 帳號 (tinalin040@gmail.com)。
- `claude-in-chrome` 擴充功能已連線。

---

## 步驟

### 1. 找 2 樣夥伴商店商品（1 食品 + 1 非食品）與 1 樣獨家品牌商品

1. 依照 `tw.shop.com/hot-deals` 或 `tw.shop.com/daily-deals` 找出符合條件的夥伴商店商品。
2. 依照品牌列表找出 1 樣獨家品牌商品（避開近 7 天重複的品牌）。
3. 蒐集每個商品的：**商品名稱**、**原價**、**優惠價**、**商品詳細介紹**，以及**至少 3 張真實吸引人的商品照片網址**（過濾並排除網站商標/Header Logo）。

### 2. 私人紀錄：寫入 Google Sheet 試算表

由於公開的 LINE Flex 卡片中不提供直接跳轉至 shop.com 購買連結的按鈕（避免客戶跳過推薦人或直接看到來源），因此所有商品的**原始網址**與**名稱**必須私下記錄於使用者的 Google Sheet 中，以便推薦人後續查詢。

**操作要求**：
- 請使用 Chrome 瀏覽器工具，打開使用者的 Google Drive / Google Sheets。
- 尋找或新建一個名為 **「美安商品貼文紀錄」** 的試算表。
- 確保該試算表已與 **`tinalin040@gmail.com`** 共享（若已是該帳號建立則不需額外共用）。
- 新增一行紀錄，寫入：**日期**、**商品名稱**、**原價/特價**、**原始商品連結**。

### 3. 生成精美文案與轉檔圖片

- **商品文案 (d)**：
  - 每樣商品必須重新編寫為**至少 5 行**、格式整齊且資訊豐富的條列式說明文案（使用 Emojis，並用換行字元 `\n` 分行）。
- **商品圖片 (i)**：
  - 下載商品主圖，若原圖為 `.avif` 或其他特殊格式，必須在本地**轉檔為 JPEG 格式**，並上傳至 Catbox（`catbox.moe`）取得公開短網址。
  - 每樣商品最多保留 **3 張** Catbox 的圖片短網址。
- **無連結按鈕**：
  - 卡片不包含「查看詳情」按鈕。URL parameters 中不加入 `l` (link) 參數以省下網址空間。

### 4. 儲存 JSON 並發送 LINE 連結

- 格式化後的 JSON 資料存至 `output/<今天日期 YYYY-MM-DD>.json`：
  ```json
  [
    {
      "name": "商品名稱",
      "price_original": "NT$xxx",
      "price_sale": "NT$xxx",
      "desc": "第1行...\n第2行...\n第3行...\n第4行...\n第5行...",
      "images": ["catbox_url1", "catbox_url2", "catbox_url3"]
    }
  ]
  ```
- 執行以下指令發送通知至小群組：
  ```bash
  .venv/Scripts/python.exe tools/send_line_message.py output/<今天日期>.json
  ```

### 5. 錯誤處理與日誌

- 任何步驟出錯都應停止，並寫入 `logs/daily_post.log` 記錄失敗原因。
