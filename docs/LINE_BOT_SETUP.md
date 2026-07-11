# LINE Bot 設定步驟

此文件是給你（人工）操作的步驟，涉及帳號登入，機器人無法代勞。完成後把取得的兩個值填進 `.env`。

目前正式使用的官方帳號是 **apple**（@376jspic），只加入一個群組「2-shop」。
Bot 每天在「2-shop」發文（含商品連結），你自己手動把貼文轉發到真正的購物群組
（原因見 PROJECT.md「LINE 訊息額度」章節：LINE 免費額度是照收訊人數算，直接發大群組
很快會用完）。

---

## 1. 開通 Messaging API

1. 登入 [LINE Official Account Manager](https://manager.line.biz/)，選擇官方帳號「apple」。
2. 左側選單「設定」→「Messaging API」→「啟用 Messaging API」（若尚未啟用）。
3. 啟用後會連動建立一個 LINE Developers 的 Provider / Channel。

## 2. 取得 Channel Access Token

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)。
2. 選擇 Provider「Tina」→ 選擇 Channel「apple」。
3. 「Messaging API」分頁 → 拉到「Channel access token」→ 按「Issue」發行一個長期 token。
4. 複製這串 token，填入 `.env` 的 `LINE_CHANNEL_ACCESS_TOKEN`。
5. 若 token 失效（出現 401 認證錯誤），回這個頁面按「Reissue（補發）」重新產生一組。

## 3. 允許 Bot 加入群組聊天

1. 回到 [LINE Official Account Manager](https://manager.line.biz/) →「設定」→「回應設定」。
2. 把「加入群組聊天」設定為「開啟」。
3. 「聊天」相關的自動回應建議關閉（只用 push message，不需要對話功能；群組裡有人講話
   不需要 Bot 回應）。

> 若發現 Bot 剛加入群組沒多久就被自動踢出、且這個設定會自己跳回「不接受邀請」，
> 這是帳號本身的問題（曾在「Tina」這個帳號上發生過，原因不明），不要一直除錯，
> 直接建一個新帳號比較快（見 memory/decisions.md [007]）。

## 4. 把 Bot 加入「2-shop」群組

1. 用手機 LINE，把官方帳號「apple」加為好友（用 QR code 或搜尋 LINE ID，在
   Official Account Manager 首頁可以找到）。
2. 進入「2-shop」群組 → 右上角選單 →「邀請」→ 選擇「apple」邀請進群組。

## 5. 取得 Group ID

LINE 沒有介面直接顯示 Group ID，需要透過 webhook 事件取得（Bot 被加入群組時會觸發
`join` 事件，payload 裡有 `groupId`）。若「2-shop」的 Group ID 已知（目前是
`Cb41942218484bc8916ee5ca35c21f316`，見下方「完成後」），通常不需要重做這步；
只有在**建立全新群組**時才需要重新取得。

我們準備了一支暫時性小工具 `tools/get_line_group_id.py` 幫你抓這個值，步驟：

1. 在專案資料夾執行（**務必加 `-u` 參數，否則輸出會被緩衝、看不到即時結果**）：
   ```
   python -u tools/get_line_group_id.py
   ```
   這會在本機啟動一個小型 HTTP 伺服器（預設 port 8787）。
2. 開新的終端機視窗，用 localtunnel 或 ngrok 建立公開網址，例如：
   ```
   npx localtunnel --port 8787
   ```
   會得到一個公開網址，例如 `https://xxxx.loca.lt`。
3. 回到 LINE Developers Console → Channel「apple」→「Messaging API」分頁 →
   「Webhook URL」填入：`https://xxxx.loca.lt/webhook`，按「Update」，再按「Verify」
   確認能連通，並把「Use webhook」打開。
4. 把 Bot 邀請進目標群組。觀察 `get_line_group_id.py` 的終端機輸出，會印出類似：
   ```
   [取得 Group ID] C1234567890abcdef1234567890abcdef
   ```
   這個值填入 `.env` 的 `LINE_GROUP_ID`。
5. 完成後可以關閉 localtunnel/ngrok 與這支小工具，Webhook URL 也可以清空
   （只用 push API，不需要長期收 webhook）。

---

## 完成後

`.env` 應該有：
```
LINE_CHANNEL_ACCESS_TOKEN=你的token
LINE_GROUP_ID=2-shop群組的group id
```

跟我說「已完成 LINE 設定」，我會幫你跑一次測試推播。
