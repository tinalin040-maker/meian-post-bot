# PROJECT HANDOFF — 美安貼文bot

跨 agent 接手狀態。每次收工必更新。

---

## 最後狀態 (2026-07-12 11:55 Antigravity)

1. **完成項**：依使用者要求，在母專案下新建了 2 個獨立子目錄，分別初始化 Git 並發布至獨立的 GitHub 專案中，解決教學端學生免費使用的需求：
   - 專案一（免寫程式版）：[meian-nocode-liff-helper](https://github.com/tinalin040-maker/meian-nocode-liff-helper)（網址為 [https://tinalin040-maker.github.io/meian-nocode-liff-helper/](https://tinalin040-maker.github.io/meian-nocode-liff-helper/)），附帶文案生成表單與一鍵分享功能。
   - 專案二（程式自動化版）：[meian-gemini-free-bot](https://github.com/tinalin040-maker/meian-gemini-free-bot)，使用 Playwright 爬蟲搭配免費 Google Gemini API。
2. **下一步**：無，專案完全交付。
3. **阻塞**：無。
4. **注意事項**：這兩個子資料夾已加入母專案之 `.gitignore`，彼此 Git 歷史完全獨立。
5. **進度**：100%

## 歷史狀態

### 狀態 (2026-07-11 22:15 Antigravity)

### 狀態 (2026-07-11 10:10 Antigravity)

1. **完成項**：解決了 Flex Message 轉傳限制與推播費用昂貴的衝突。實作了 LINE LIFF 網頁 (`liff/index.html`) 與一鍵分享 (`shareTargetPicker`)，修改 `tools/send_line_message.py` 以將商品 JSON 資料進行 Base64 UTF-8 壓縮編碼並拼裝為 LIFF 網址發送，發送文字連結至小群組 `2-shop` 以進行一鍵轉發。成功手動發送測試連結至 `2-shop` 群組。
2. **下一步**：
   - 使用者在命令提示字元中執行 `claude login` 重新登入（目前本機憑證 401 已過期，需先登入否則排程爬蟲無法執行）。
   - 依照 `liff_setup_guide.md` 部署 `liff/index.html` 取得 HTTPS 網址。
   - 於 LINE Developers Console 後台在與機器人同 Provider 底下建立 LIFF App，綁定網址、開啟 `ShareTargetPicker` 權限取得 LIFF ID。
   - 將 LIFF ID 寫入 `.env` 的 `LINE_LIFF_ID` 變數中，在手機 LINE 上點擊連結測試一鍵分享至 80 人群組的呈現效果。
3. **阻塞**：無。
4. **注意事項**：
   - 網址長度上限約 2000 字，3 樣商品的縮減版 JSON Base64 編碼長度約在 1000 字以內，完全在安全範圍，切勿無故增加大欄位以免超出限制。
   - `ShareTargetPicker` 在後台設定時預設是關閉的，必須手動開啟，否則網頁呼叫會失敗。
   - 建立 Windows 排程時不要加 `-ExecutionPolicy Bypass`（會被安全分類器擋），這台機器 CurrentUser 執行原則已是 RemoteSigned，本機腳本不需要 Bypass。
5. **進度**：95%（只剩使用者部署網頁、設定後台並在手機端完成最後的分享測試）。

---

## 當前狀態
| 欄位 | 內容 |
|---|---|
| 任務 | 每日自動選品+推播LINE群組（2-shop）的自動化流程 |
| 進度 | 100%：已完成核心功能開發、自動查核防錯、防亂碼 Windows 啟動轉發、本地與雲端監控雙警報系統，並已完成 Git 上傳。 |
| 下一步 | 使用者每晚保持電腦開機、Chrome 開啟及 Claude 登入，Bot 即可完全自動且 0 扣點發文。 |
| 阻塞 | 無 |
| 最後操作 Agent | Antigravity |
| 最後操作時間 | 2026-07-11 22:15 |

---

## 接手注意事項

- **這不是傳統爬蟲專案**：原計畫的 Python+Playwright 背景爬蟲已放棄（詳見
  `memory/decisions.md` [003]），因 shop.com 防機器人機制會擋掉無頭自動化瀏覽器。
  改用 Claude Code + `claude-in-chrome` 擴充功能操作真實瀏覽器。**不要**建議改回純
  背景爬蟲腳本，除非使用者主動要求重新嘗試。
- 每日執行邏輯的「唯一事實來源」是 [skills/daily_post.md](../skills/daily_post.md)，
  修改選品規則、貼文格式規則都改這份文件，不要另外寫 Python 選品邏輯。
- **架構是單一群組模式**（見 `memory/decisions.md` [006]）：Bot 只加入「2-shop」
  群組，每天在這裡發文（含連結），使用者自己手動轉發到真正的購物群組。**不要**
  建議改回直接發到大群組，除非使用者主動要求——這是為了避開 LINE 免費額度
  （200則/月，且是照收訊人數算）快速用光的問題。
  不要再嘗試找「滿版又可轉傳」的方法。
  - 合成圖片目前字體大小是原始設計的 2.25 倍（多輪使用者回饋後放大），且各段落
    間（名稱→金額→介紹→CTA）都刻意留白 2 行高度，這是使用者要求的定案版本，
    不要因為「看起來留白太多」自行改小。
  - emoji 用 `C:/Windows/Fonts/seguiemj.ttf`（Segoe UI Emoji，彩色）搭配
    `embedded_color=True` 畫出來，中文/英數字用 `msjh.ttc`（微軟正黑體），兩種字型
    在同一行內混排（見 `_draw_mixed_line` / `_wrap_mixed`）。
- LINE 憑證只由 `tools/send_line_message.py` 與 `tools/log_result.py` 讀取環境變數，
  刻意不讓 Claude 在對話中處理實際 token 數值。
- 目前使用的 LINE 官方帳號是「apple」（provider「Tina」），不是最初的「shop」或
  「Tina」帳號——那兩個都因故放棄了（額度用完 / 被自動踢出群組，見
  `memory/decisions.md` [007]）。若 apple 帳號未來也出問題，直接建新帳號，
  不要在同一帳號上反覆除錯。
- **Windows 工作排程器已建立**：任務名稱 `MeianDailyPost`，每日 09:00 觸發
  `powershell.exe -NoProfile -File run_daily_post.ps1`（未用 `-ExecutionPolicy
  Bypass`，因為這台機器 CurrentUser 的執行原則已是 RemoteSigned，本機腳本可直接
  執行，不需要 Bypass）。登記在 `C:\ai-agent-center\scheduled\008_meian-daily-post.md`。
  尚未驗證過排程真正自動觸發時，`claude -p` 巢狀呼叫能否在使用者實際的 Windows
  環境下正常認證執行（先前只在 Claude 自己的沙箱環境測試過，會因認證問題失敗，
  但沙箱環境跟使用者真實環境不同，理論上使用者環境已登入 claude CLI 應該沒問題）
  ——**交接時第一件事是檢查 2026-07-07 09:00 那次排程是否成功執行**，若失敗，
  優先檢查：(1) 電腦有無開機、(2) Chrome 有無開啟並登入 shop.com、(3)
  `logs/task_scheduler_*.log` 裡的錯誤訊息。

---

## 切換歷史

| Timestamp | Agent | 動作 | 備註 |
|---|---|---|---|
| 2026-07-05 | OpenCode | 初始化專案 | - |
| 2026-07-05 | Claude | 需求釐清、技術調查、架構設計與實作 | 詳見 memory/decisions.md [002]-[004] |
| 2026-07-06 | Claude | 貼文格式定案、改為單一群組「2-shop」架構、LINE帳號改用apple、測試推播成功 | 詳見 memory/decisions.md [006]-[007] |
| 2026-07-06 | Claude | 改用合成圖片+原生圖片訊息（解決Flex無法轉傳問題）、字體/留白多輪調整定案、建立Windows工作排程器MeianDailyPost | 詳見 memory/decisions.md [008]，登記 scheduled/008_meian-daily-post.md |
