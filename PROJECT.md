# PROJECT — 美安貼文bot

給 AI agent 讀的專案元資料。

---

## 基本資訊
| 欄位 | 內容 |
|---|---|
| 名稱 | 美安貼文bot |
| 用途 | 每天自動選出2樣夥伴商店划算商品+1樣獨家品牌商品，發到LINE的「2-shop」群組，使用者自己轉發到真正的購物群組 |
| 建立日期 | 2026-07-05 |
| 建立 Agent | OpenCode |
| 狀態 | 核心流程已跑通並手動測試成功，Windows 工作排程器已設定每天 9:00 自動執行（任務名稱 MeianDailyPost），尚待驗證首次自動觸發是否正常 |

---

## 目標

每天早上 9:00：
1. 選出 2 樣夥伴商店的划算商品（1 食品 + 1 非食品，價格必須真實可查證）
2. 選出 1 樣獨家品牌商品（美安台灣品牌 our-brands）
3. 每樣商品各自組成一則貼文：3張照片+商品名稱/原價/優惠價/介紹文案/固定 CTA 合成
   一張圖片，用 LINE 原生「圖片訊息」發送，後面接一則純文字訊息放商品連結
4. 三則貼文都發到 LINE 的「2-shop」群組（Bot 只加在這一個群組）
5. 使用者自己手動把貼文從「2-shop」轉發到真正的購物群組

**不是**自動發到大群組——大群組交給使用者手動轉發，理由見下方「LINE 訊息額度」。

---

## 技術棧
- 語言：PowerShell（排程進入點）+ Python（LINE 推播、log 工具）
- 核心機制：**Claude Code Agent + claude-in-chrome 瀏覽器擴充功能**（見下方「為什麼不用背景爬蟲腳本」）
- 資料來源：
  - tw.shop.com（hot-deals、daily-deals、info/our-brands，找候選商品跟明確價格）
  - 候選商品的**外部店家自己的網站**（或 shop.com 品牌商品詳情頁）：抓正式的商品名稱、
    原價/優惠價、真實商品介紹、至少3張商品圖片
- 推播：LINE Messaging API push message，原生圖片訊息（照片+文字合成一張圖，上傳到
  catbox.moe 取得公開網址）+ 純文字連結訊息
- 排程：Windows 工作排程器，每天 09:00 觸發 `run_daily_post.ps1`（任務名稱 `MeianDailyPost`，
  已於 2026-07-06 設定，見 `scheduled/008_meian-daily-post.md`）

---

## 外部依賴
- API：LINE Messaging API（見 docs/LINE_BOT_SETUP.md）
  - 目前使用的官方帳號：**apple**（@376jspic），provider 是「Tina」
  - `.env` 只有 `LINE_CHANNEL_ACCESS_TOKEN`、`LINE_GROUP_ID`（"2-shop" 群組）兩個變數
- 服務：Claude Code CLI（需已登入、Chrome 擴充功能已連線）
- 帳號：shop.com 會員登入（用電腦上真實 Chrome 瀏覽器維持登入狀態）

---

## 重要技術決策

### 1. 為什麼不用背景爬蟲腳本

原始設計是 Python + Playwright 背景腳本。**實測後放棄**：tw.shop.com 有防機器人機制，
無頭/自動化 Playwright 瀏覽器大約瀏覽 3 個頁面就會被封鎖（顯示「您的IP已經被停用」），
換瀏覽器指紋、真的裝 Chrome 都沒用；但同一台電腦的**真實 Chrome 瀏覽器**完全不受影響。

**方案**：改用 Claude Code Agent 透過 `claude-in-chrome` 擴充功能操作真實已登入的 Chrome
瀏覽器（如同人工瀏覽），取代獨立自動化爬蟲行程。每日流程寫在
[skills/daily_post.md](skills/daily_post.md)，由 [run_daily_post.ps1](run_daily_post.ps1)
呼叫 `claude -p` 執行。**外部店家自己的網站**（例如 chenfood88.com）也是用同一支真實瀏覽器
進去看，可以放心點進去抓商品詳情（名稱/價格/圖片），不受上述防機器人限制。

### 2. LINE 訊息額度：為什麼只發一個小群組，不直接發大群組

LINE 免費方案「訊息則數」是照**收到訊息的人數**算，不是照「發送次數」算：
發一則訊息到 100 人的群組 = 消耗 100 則額度。第一次直接測試發到真正的大群組（30~100人）
就在推播 2、3 樣商品後把免費額度（200則/月）用光，導致貼文發送失敗。

**解法**：Bot 只加入一個小群組「2-shop」（成員很少），每天在這裡發文，使用者自己手動
把內容**轉發**到真正的購物群組——LINE 的「轉發」是使用者自己的操作，不會消耗 Bot 的
訊息額度，从根本上避開這個問題，也不需要升級付費方案。

### 3. LINE 官方帳號選用歷程（教訓，供之後接手參考）

- 一開始建立帳號「shop」，發到兩個真正的群組（主要購物群組+存檔群組），測試沒幾次
  就把免費額度用光（見上一點）。
- 改用既有帳號「Tina」時，發現這個帳號一直被 LINE 系統自動踢出剛加入的群組，且
  「加入群組或多人聊天室」設定會自己被重設回「不接受邀請」——原因不明，懷疑跟這個
  帳號本身的歷史/信譽狀態有關，不是我們的操作問題。**放棄使用 Tina**。
- 最後新建帳號「apple」（provider 一樣掛在 Tina 這個 provider 底下），沒有上述踢出問題，
  順利發送成功。**目前正式使用的是 apple。**
- 教訓：如果之後又遇到「Bot 剛加入群組就消失」的狀況，不要一直在同一個帳號上除錯，
  直接建一個全新帳號比較快。

---

## 貼文格式規則（重要）

1. 每樣商品是**一張合成圖片**：3張照片橫排在上面 + 商品名稱 + 原價(劃線,選填) +
   優惠價 + 吸引人的介紹文案 + 固定 CTA「馬上私訊 Ethan我，優惠價格就入手！」全部合成
   一張圖，用 LINE 原生「圖片訊息」發送（`tools/compose_image.py` 用 Pillow 合成，
   上傳到 catbox.moe 免帳號圖床取得公開網址）。
2. 圖片後面**再接一則純文字訊息**只放商品連結——純文字訊息裡的網址才能長按複製或
   直接轉發。
3. **改用原生圖片訊息、不用 Flex Message 的原因**：Flex Message（圖文合一卡片）
   在 LINE 用戶端長按沒有「轉傳」選項，使用者沒辦法把貼文分享到其他群組——這是
   LINE 平台限制。原生圖片訊息+文字訊息才能被長按轉傳、也能多選一起轉發。
   （詳見 memory/decisions.md 相關記錄）
4. 三樣商品**各自獨立發送**，不合併成一則。
5. **價格一律照抄來源頁面，不做任何換算**，多重價格要先判斷清楚是哪個方案，沒把握就
   跳過這個商品——寧可湊不滿3樣，也不能價格出錯（詳見 skills/daily_post.md）。
6. 圖片：夥伴商店商品要進到**該店家自己的網站**商品詳情頁抓（因為 shop.com promo banner
   只有1張圖），品牌商品從 shop.com 品牌商品頁的縮圖相簿抓，都要求至少3張。
7. 合成圖片使用的字型：`C:/Windows/Fonts/msjh.ttc`（微軟正黑體），文字中的 emoji
   會被過濾掉不畫進圖片（該字型不支援彩色 emoji 字符，畫出來會變成方框亂碼）。

---

## 限制 / 注意事項

- stores-a-z / hot-deals 上的促銷文案要有**明確價格數字**才算候選，「85折」「輸入折扣碼」
  這種店家層級優惠不算。
- Playwright 若之後要用在**其他**專案：venv 若建立在含中文字元路徑的資料夾下，瀏覽器會
  `spawn UNKNOWN` 失敗（Node driver 對 CJK 路徑的已知問題），需把 venv 建在純 ASCII 路徑。
  本專案已不使用 Playwright，此為留給其他專案的教訓。
- 操作 LINE Developers / Official Account Manager 網頁時，切換 radio 按鈕用滑鼠座標點擊
  常常沒反應，要改用 JS 找到對應的 `<label for="...">` 呼叫 `.click()` 才穩定觸發。

---

## 相關連結
- [docs/LINE_BOT_SETUP.md](docs/LINE_BOT_SETUP.md) — LINE Bot 設定步驟（需使用者操作）
- [skills/daily_post.md](skills/daily_post.md) — 每日執行流程完整指令
- [run_daily_post.ps1](run_daily_post.ps1) — 排程進入點（尚未實際設定 Windows 排程）
- [tools/send_line_message.py](tools/send_line_message.py) — 組 Flex 卡片並推播
