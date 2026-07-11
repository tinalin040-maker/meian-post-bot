# DECISIONS — 美安貼文bot

ADR 風格紀錄。

---

## 模板
```
### [編號] 標題
- Date:
- Agent:
- 背景:
- 決策:
- 理由:
- 影響:
```

---

## 紀錄

### [001] 專案初始化
- Date: 2026-07-05
- Agent: OpenCode
- 背景: 新專案 美安貼文bot 建立
- 決策: 採用 AI Agent Center 標準結構
- 理由: 跨 agent 接手一致性
- 影響: 後續所有 agent 依本中心規則操作

### [002] 選品資料來源縮小範圍
- Date: 2026-07-05
- Agent: Claude
- 背景: 使用者原始需求是從 stores-a-z 挑2樣划算商品。實測發現該頁只有店家促銷文案
  （常是「85折」「輸入折扣碼」這類店家層級優惠，非單一商品價格），且商品詳情頁在
  外部夥伴商店網站（各家平台不同、結構不一，如 SHOPLINE、自架站），無法穩定抓取。
- 決策: 「划算商品」改為：優先用 hot-deals（最新促銷優惠）中文案有明確價格數字的項目，
  不足則用 daily-deals（每日一物，官方每天一個精選商品）補。三者皆為 shop.com 自己
  網域內的頁面，格式固定可靠。
- 理由: 使用者確認選項「先嘗試最新促銷優惠中文案有寫明確價格的商家，不足再用每日一物補」
- 影響: 部分日子可能只湊到 1 則划算商品（如實記錄，不編造）。

### [003] 放棄 Playwright 背景爬蟲，改用 Claude Code + 真實瀏覽器
- Date: 2026-07-05
- Agent: Claude
- 背景: 原計畫用 Python + Playwright 背景腳本，由 Windows 工作排程器直接執行。
  實測發現 tw.shop.com 有防機器人機制：無頭/自動化瀏覽器（含改用電腦上真正安裝的
  Chrome、加反偵測參數、已登入 session）大約瀏覽 3 個頁面後就被封鎖；但同一台電腦的
  真實 Chrome 瀏覽器（人工/擴充功能操作）完全不受影響。
- 決策: 改用 Claude Code Agent 透過 `claude-in-chrome` 擴充功能操作真實已登入的
  Chrome 瀏覽器來瀏覽/判斷網頁內容，取代獨立的自動化爬蟲行程。排程進入點改成
  `run_daily_post.ps1` 呼叫 `claude -p`，執行指令寫在 `skills/daily_post.md`。
- 理由: 使用者在得知風險後選擇「改用 AI 瀏覽器代理（真實Chrome，最穩定）」。
- 影響:
  - 執行時電腦必須開機、Chrome 需已開啟並登入、擴充功能需已連線，否則流程會失敗。
  - 每天執行會有少量 Claude API 費用。
  - LINE 推播/log 記錄保留為固定 Python 腳本（`tools/send_line_message.py`、
    `tools/log_result.py`），憑證只由這兩支腳本讀取環境變數，不讓 Claude 看到實際數值。
  - 舊的 `src/scrape.py`、`scripts/setup_login.py`、Playwright 依賴已移除。

### [004] 新增第二個 LINE 群組（含購買連結）
- Date: 2026-07-05
- Agent: Claude
- 背景: 使用者追加需求，除了主要購物群組（不含連結）外，還要在另一個群組推播完全
  一樣的3樣商品資訊，但每樣多附上該商品頁面的連結（含使用者的推薦代碼，用於導購/
  賺取回饋）。
- 決策: `tools/send_line_message.py` 改為同時處理兩個群組：`LINE_GROUP_ID`（主要，
  不含連結按鈕）與 `LINE_GROUP_ID_LINKS`（同樣3樣商品，每樣多一個「前往這個商品」
  按鈕）。items.json 新增 `link` 欄位，且**不去掉查詢字串**（因為那是推薦代碼，
  跟圖片網址的追蹤參數需要去掉是相反的處理）。
- 理由: 使用者確認「完全一樣的3樣商品資訊，只是多加連結」「連結=你推薦那個商品的
  網頁連結」。
- 影響: `docs/LINE_BOT_SETUP.md` 需要把 Bot 加入兩個群組、取得兩個 Group ID；
  `.env.example` 新增 `LINE_GROUP_ID_LINKS`；`skills/daily_post.md` 新增蒐集
  `link` 欄位的步驟。

### [005] Playwright venv 路徑教訓（僅供未來專案參考，本專案已不使用）
- Date: 2026-07-05
- Agent: Claude
- 背景: 測試 Playwright 時，若 venv 建立在含中文字元的資料夾路徑下
  （例如本專案 `C:\ai-agent-center\projects\美安貼文bot\.venv`），
  `browser.launch()` 會拋出 `spawn UNKNOWN` 錯誤，換到純 ASCII 路徑
  （`C:\ai-agent-center\.venvs\xxx`）建立 venv 後問題消失。
- 決策: 記錄此教訓，供其他專案若用到 Playwright/Node-based 工具時參考。
- 理由: 這是 Windows + Node 對 CJK 路徑處理的已知限制，非本專案程式碼問題。
- 影響: 無（本專案已改用真實瀏覽器方案，不再需要 Playwright）。

### [006] 貼文格式改為「Flex卡片+連結另發純文字」，且改成只發一個小群組
- Date: 2026-07-06
- Agent: Claude
- 背景: 經過多輪使用者回饋（範本文案、CTA文字、照片要3張、連結要能複製），貼文格式
  最終定案為：每樣商品一張 Flex 卡片（3張圖橫排+名稱/原價/優惠價/介紹+CTA），卡片
  後面接一則純文字訊息放連結（Flex裡的文字連結在LINE不好長按複製/轉發）。
  另外，第一次直接推播到真正的大群組（30~100人）時，2、3樣商品就把LINE免費訊息
  額度（200則/月）用光了——因為LINE的額度是照「收到訊息的人數」算，不是照發送次數。
- 決策: 改成 Bot 只加入一個小群組「2-shop」，每天發文在這裡，使用者自己手動轉發到
  真正的購物群組。`.env` 精簡回只需要 `LINE_CHANNEL_ACCESS_TOKEN`、`LINE_GROUP_ID`
  兩個變數（不再需要 LINE_GROUP_ID_LINKS 雙群組邏輯）。
- 理由: 使用者明確表示「我要更改遊戲規則...之後你只要在2-shop群組po貼文...我自己
  手動發到群組」。
- 影響: `tools/send_line_message.py` 大幅簡化（不再處理 with_link/without_link 兩種
  變體，改成固定都附連結，用獨立文字訊息發送）；`skills/daily_post.md`、PROJECT.md
  同步更新。

### [007] LINE 官方帳號選用：shop → Tina → apple
- Date: 2026-07-06
- Agent: Claude
- 背景: 帳號「shop」額度用完後，使用者要求改用既有帳號「Tina」，但 Tina 出現詭異行為：
  每次邀請進「2-shop」群組後很快被自動踢出，且「允許機器人加入群組」設定會自己被
  重設回「不接受邀請」，重複發生多次（不是操作失誤，是外部系統行為）。花了不少來回
  都無法穩定讓 Tina 留在群組裡。
- 決策: 放棄 Tina，新建一個全新帳號「apple」（一樣掛在 Tina 這個 provider 底下），
  改用 apple 之後沒有再出現被踢出的問題，推播成功。
- 理由: 使用者決定「再創一個新的頻道」而非繼續在 Tina 上除錯。
- 影響: `.env` 的 `LINE_CHANNEL_ACCESS_TOKEN` 最終指向 apple 帳號（Channel ID
  2010620393，@376jspic）。若之後又遇到「Bot剛加入群組就消失」的狀況，建議直接
  換新帳號，不要在同一個帳號上反覆除錯設定。

### [008] 放棄 Flex Message，改用「合成圖片+原生圖片訊息」
- Date: 2026-07-06
- Agent: Claude
- 背景: 使用者實測發現，[006] 採用的 Flex Message（照片+文字合一卡片）在 LINE 用戶端
  長按沒有「轉傳」選項，導致無法把貼文分享/轉發到其他群組——這正好違背整個「單一
  2-shop群組+使用者手動轉發」架構的前提（見 [006]）。查證後確認這是 LINE 平台限制：
  Flex/Template 這類互動式訊息本來就不支援長按轉傳，只有純文字、圖片、影片、貼圖等
  原生訊息類型才支援。
- 決策: 改用 `tools/compose_image.py`（Pillow）把 3 張商品照片+商品名稱/原價/優惠價/
  介紹文案/CTA 全部合成一張圖片，上傳到 catbox.moe（免帳號圖床）取得公開網址，再用
  LINE 原生「圖片訊息」發送；後面一樣接一則純文字訊息放連結。圖片訊息和文字訊息都
  能被使用者長按轉傳，也能多選一起轉發。
- 理由: 使用者明確要求「你的貼文要讓我能分享到其他群組」。三個方案中選擇「免費圖床」
  （優點：不需要註冊帳號/申請API Key，設定最簡單；取捨：依賴 catbox.moe 這個第三方
  免費服務的穩定性，若之後常態性失敗或服務關閉，可考慮換成使用者自己控制的 Netlify
  靜態空間，見對話中討論過的替代方案）。
- 影響: `tools/send_line_message.py` 移除所有 Flex Message 相關程式碼，改呼叫
  `tools/compose_image.py` 的 `build_composite_image()` + `upload_to_catbox()`；
  新增 Pillow 依賴（`requirements.txt`）；`skills/daily_post.md`、PROJECT.md 同步
  更新貼文格式規則；合成圖片用字型 `C:/Windows/Fonts/msjh.ttc`，文字中的 emoji 會
  被正規表示式過濾掉（該字型無法正確畫出彩色 emoji，會變成方框亂碼）。

### [009] 貼文視覺格式定案：emoji混排字型、字體2.25倍、加大留白；確認排程免ExecutionPolicy Bypass
- Date: 2026-07-06
- Agent: Claude
- 背景: [008] 上線後使用者實測發現兩個問題：(1) msjh.ttc 無法畫出彩色 emoji（會變
  方框亂碼），原本用正規表示式整段過濾掉，但使用者希望保留原文案裡的 emoji 讓畫面
  活潑一點；(2) 圖片訊息在聊天室裡顯示縮圖太小，使用者一度希望能比照 Flex 卡片
  「自動滿版顯示」，但實測+討論後確認 LINE 平台限制：滿版自動顯示（Flex/Imagemap
  這類「範本訊息」）與長按轉傳，兩者互斥，任何訊息類型都無法兩者兼得，這是 LINE
  對訊息類型的固定規則，不是排版或程式問題。
- 決策:
  1. emoji 改用 `C:/Windows/Fonts/seguiemj.ttf`（Segoe UI Emoji，彩色字型）搭配
     Pillow 的 `embedded_color=True` 畫出來，跟中文字型（msjh.ttc）在同一行內
     混排（`_wrap_mixed` / `_draw_mixed_line`），不再整段過濾 emoji。
  2. 字體大小經多輪回饋後，最終是最初版本的 2.25 倍（1.5倍→再1.5倍）。
  3. 名稱→金額、金額→介紹文案、介紹文案→CTA 之間，各自加大留白（約2行高度的間距）。
  4. 確認「滿版顯示」與「可轉傳」互斥後，使用者選擇維持可轉傳版本（原生圖片訊息），
     接受圖片要點開才能看清楚的取捨——**之後不要再嘗試找兩全其美的方法，已經確認
     不存在**。
- 理由: 使用者多輪明確回饋（放大字體、加大留白、確認互斥後選擇可轉傳優先）。
- 影響: `tools/compose_image.py` 全面改寫，新增 `_is_emoji`/`_emoji_font`/
  `_wrap_mixed`/`_draw_mixed_line`/`_draw_run`，emoji 判斷用正規表示式範圍比對
  單一字元；同時建立 Windows 工作排程器任務 `MeianDailyPost`（每日09:00觸發
  `run_daily_post.ps1`），**特別注意**：建立時不要用 `-ExecutionPolicy Bypass`
  （會被安全分類器擋下，因為使用者沒有明確授權這個旗標）——這台機器 CurrentUser
  的 PowerShell 執行原則已經是 `RemoteSigned`，本機自己建立的 .ps1 腳本本來就能
  直接執行，不需要 Bypass，用 `powershell.exe -NoProfile -File <path>` 即可。

### [010] 導入 LINE LIFF 一鍵轉發滿版圖文卡片（解衝突：免費 + 滿版）
- Date: 2026-07-11
- Agent: Antigravity
- 背景: 使用者需要滿版圖文（Flex Message）卡片發送到 80 人大群組，但若由機器人直接發送，每次發送會扣除 80 點 API 額度（很快就會超出每月 200 點的免費限制）；然而若退而求其次讓使用者手動轉發，LINE 又限制了 Flex 訊息無法長按轉傳。這兩者產生了功能與費用上的核心衝突。
- 決策: 導入 LINE LIFF 一鍵分享功能。建立一個靜態網頁 `liff/index.html`（自動解析 URL 裡的 Base64 商品壓縮資料並彈出 `shareTargetPicker` 分享卡片），並修改 `tools/send_line_message.py` 不再合成 Pillow 圖片，改為將商品資料壓縮轉 Base64 並封裝成 LIFF 分享連結，每天早上僅推播一則純文字通知（內含該連結）至小群組 `2-shop`。
- 理由: LINE LIFF 呼叫 `shareTargetPicker` 發送訊息，在技術上是屬於「使用者本人」傳送私訊，完全免費、不消耗官方帳號點數，且支援發送 Flex Message。這是唯一能同時滿足「滿版圖文」且「免費 0 點發到大群組」的方法。
- 影響:
  - 廢棄了原有的圖片合成 (`compose_image.py`) 推播方式，但保留了該檔案供備用。
  - 使用者必須一次性將 `liff/index.html` 部署至 HTTPS 平台，並在 LINE Developers 後台註冊 LIFF 頻道取得 LIFF ID 並寫入 `.env`。
  - `run_daily_post.ps1` 增加了 `$null |` 的 stdin 管道轉發，並改用動態路徑解析，以排除 CJK 編碼造成的執行錯誤。

### [011] 自動查核防錯機制與本機+雲端雙向警報監控系統
- Date: 2026-07-11
- Agent: Antigravity
- 背景: 使用者對於貼文金額、網址連結有 100% 正確性的嚴格要求（金額錯誤對業務有重大負面影響）。同時使用者需要在每天發文時間 19:45 左右，如果電腦沒開機、或 Chrome/Claude 執行失敗時，能即時收到通知警報，防止貼文中斷。並且由於 Windows 排程器在處理中文路徑時會產生 CP950/UTF-8 字元亂碼 bug，導致排程靜默失效（執行碼為 1）。
- 決策: 
  1. **自動校驗**：在寫入 JSON 前新增價格與連結的防呆校驗（比對原始特價與網頁價格、檢測 URL HTTP 狀態碼、限制 5 行文案格式），校驗失敗則拋出異常阻斷發送。
  2. **本地警報**：新增 `tools/send_alert.py` 本地 LINE 警報機制，並修改本機 `run_daily_post.ps1` 啟動腳本，以 `try-catch` 包裹主程序。若執行失敗，會立刻透過 LINE Push API 發送警報至 `2-shop` 小群組。
  3. **雲端定時監控**：新增 GitHub Actions 每日 UTC 12:00（台北時間 20:00，排程後 15 分鐘）執行的 `.github/workflows/monitor.yml` 雲端監控任務。呼叫 `tools/cloud_monitor.py` 連線並檢查 Google Sheets 中是否寫入今日排程資料，若無（代表本機沒開機或斷電當機），雲端直接發送 LINE 警告訊息。
  4. **排程路徑相容性修復**：建立 ASCII 純英文字元路徑的啟動轉發檔 `C:\ai-agent-center\run_meian_bot.bat`（內部設定 `cd` 切換至中文目錄），並另存 `run_daily_post.ps1` 為 UTF-8 BOM 格式，徹底避開 Windows 排程器與 PowerShell 5.1 對中文路徑及字元的亂碼 Bug。
- 理由: 提供軍規級的自動校驗與雙重防漏洞警報機制，並徹底排除 Windows 系統平台的亂碼啟動 bug，保證系統極致穩定。
- 影響: 
  - 本機與雲端監控均已整合 LINE 與 Google Sheets APIs，並通過手動與雲端實測執行，回傳 exit code 0，穩定可靠。
  - 將專案推送至 GitHub 公開專案庫託管（安全忽略私密 env 金鑰，金鑰已上傳至 GitHub Secrets 安全加密保存）。


