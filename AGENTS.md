# AGENTS.md — 美安貼文bot

本檔引用 AI Agent Center 通用規則。

@C:\ai-agent-center\AGENTS.md

---

## 觸發詞（所有 agent 必遵守，不依賴上方引用是否展開）

聽到下列觸發詞，**立刻用絕對路徑 Read 對應檔案並依其流程執行**：

| 觸發詞 | 動作 |
|---|---|
| 開工 | Read `C:\ai-agent-center\skills\start_work.md` 並執行 |
| 收工 | Read `C:\ai-agent-center\skills\finish_work.md` 並執行 |
| 初始化 | Read `C:\ai-agent-center\skills\init_project.md` 並執行 |
| DASHBOARD / 總覽 / 儀表板 | Read `C:\ai-agent-center\skills\dashboard.md` 並執行 |

---

## 本專案特殊規則
- ⚠️ **價格與連結 100% 正確性鐵律**：本專案的價格具有極高敏感性。不論是自動排程選品或手動補發，若因網頁防爬、重定向或任何原因無法取得 100% 精確的商品價格與連結時，**必須立刻丟出 Exception 中斷執行並發送 LINE 警報**，絕對不允許使用任何 AI 推估、猜測、或模擬的模糊金額。


---

## 本專案技術棧 / 限制

請見 [PROJECT.md](PROJECT.md)。
