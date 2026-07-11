# TODO — 美安貼文bot

| 狀態 | 建立 Agent | 建立日期 | 內容 | 負責 Agent |
|---|---|---|---|---|
| [x] | Claude | 2026-07-05 | 完成 LINE Bot 設定文件、爬蟲/選品邏輯、LINE推播腳本、排程進入點 | Claude |
| [x] | Claude | 2026-07-05 | 使用者完成 docs/LINE_BOT_SETUP.md，填入 .env | 使用者 |
| [x] | Claude | 2026-07-06 | 貼文格式定案（Flex卡片+CTA+獨立連結訊息），改為單一「2-shop」群組架構 | Claude |
| [x] | Claude | 2026-07-06 | 手動測試推播3樣商品到「2-shop」群組，確認成功 | Claude |
| [x] | Claude | 2026-07-06 | 使用者確認「2-shop」群組收到的貼文顯示正常 | 使用者 |
| [x] | Claude | 2026-07-06 | 改用合成圖片+原生圖片訊息取代Flex卡片（解決無法轉傳問題），字體/留白多輪調整定案 | Claude |
| [x] | Claude | 2026-07-06 | 用 schtasks 建立每天9:00排程（MeianDailyPost），登記到 SCHEDULED_INDEX.md | Claude |
| [ ] | Claude | 2026-07-06 | 驗證明天(2026-07-07)09:00排程首次自動觸發是否正常執行完整流程 | - |

---

## 狀態符號
- `[ ]` 待辦
- `[/]` 進行中
- `[x]` 完成
- `[-]` 取消
