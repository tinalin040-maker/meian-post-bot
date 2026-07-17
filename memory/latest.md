# LATEST — 美安貼文bot

每次收工後追加。超過10列自動歸檔至 memory/archive/。

| Timestamp | Agent | 摘要 |
|---|---|---|
| 2026-07-17 20:32 | Antigravity | 依反映修正今日發布櫻桃品名加標規格 (500g 塑膠盒裝)，更新 Sheets 並重新合成圖卡推播新連結成功；更新貼文規範要求未來有規格商品必須標註。 |
| 2026-07-17 19:45 | Claude | 排程觸發（19:45 task_scheduler，Gemini API 腳本失敗後 fallback 至 Claude CLI）自動執行每日貼文流程成功：選品（食品:買嗨森美國加州華盛頓櫻桃禮盒NT$590、非食品:伊德生活冰峰床組NT$2,800、獨家品牌:Pro-Collagen魔妍膠原蛋白粉NT$1,425，避開近7天已用過的築地一番鮮/小日常寢居/Isotonix/Tower+等品牌）、下載轉檔8張圖片上傳Catbox、寫入Google Sheets 3筆紀錄、成功發送LIFF分享連結至2-shop群組（https://tinyurl.com/25dootft）。 |

| 2026-07-16 21:32 | Antigravity | 修復 Windows 排程引導批次檔中的中文編碼亂碼，改用絕對路徑 powershell 呼叫；手動以 headed playwright 下載今日促銷並以 Python 補發貼文成功，寫 Sheets 與 LINE。 |
| 2026-07-14 21:30 | Antigravity | 新增圖床 Fallback 機制與補跑今日貼文成功；修復 liff.login() 參數並新增 cb 參數解決手機 LINE WebView 快取舊網頁導致的 HTTP 400 錯誤，同步更新各專案並已 PUSH 上線。 |
| 2026-07-12 19:45 | Claude | 排程觸發（19:45 task_scheduler）自動執行每日貼文流程成功：選品（食品:築地一番鮮買1送1_9.5ROW華盛頓櫻桃NT$999、非食品:安德森保羅海鹽小蘇打雙效亮白牙膏NT$298、品牌:柔雅柔膚沐浴露Royal SpaNT$662定期購，避開近7天已用過的易善/Isotonix品牌）、下載轉檔9張圖片上傳Catbox、寫入Google Sheets 3筆紀錄、成功發送LIFF分享連結至2-shop群組。順手修正 `tools/write_to_sheets.py` 寫死讀取2026-07-11.json的bug，改為動態讀取當日日期的json，否則之後每次自動同步都會寫入舊資料。 |

