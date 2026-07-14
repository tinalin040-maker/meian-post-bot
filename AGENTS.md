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

（在此寫入本專案特有的規則。若無，保持空白。）

---

## 本專案技術棧 / 限制

請見 [PROJECT.md](PROJECT.md)。
