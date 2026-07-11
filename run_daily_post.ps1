# 由 Windows 工作排程器每天 09:00 觸發。
# 前置需求：這台電腦的 Chrome 必須已開啟並登入 shop.com，Claude Code 的 Chrome 擴充功能已連線。

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

$WorkflowDoc = Get-Content -Raw -Encoding UTF8 (Join-Path $ProjectDir "skills\daily_post.md")
$Prompt = @"
請依據以下每日貼文流程文件的指示，立刻執行今日的美安商品貼文自動化流程。

【指示】
請在 Chrome 瀏覽器中執行選品，並寫入 Google Sheets 紀錄，完成圖片下載、轉檔與上傳至 Catbox，最後呼叫 `tools/send_line_message.py` 完成 LINE 推播。

【流程文件內容】
$WorkflowDoc
"@

$LogDir = Join-Path $ProjectDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$RunLog = Join-Path $LogDir ("task_scheduler_{0}.log" -f (Get-Date -Format "yyyy-MM-dd_HHmmss"))

$AllowedTools = @(
    "Bash(python *)",
    "Bash(.venv/Scripts/python.exe *)",
    "Write",
    "Read",
    "Glob",
    "mcp__claude-in-chrome__navigate",
    "mcp__claude-in-chrome__get_page_text",
    "mcp__claude-in-chrome__read_page",
    "mcp__claude-in-chrome__tabs_context_mcp",
    "mcp__claude-in-chrome__tabs_create_mcp",
    "mcp__claude-in-chrome__javascript_tool"
)

try {
    # 執行 Claude Bot
    $null | claude -p $Prompt `
        --chrome `
        --allowedTools $AllowedTools `
        *> $RunLog

    if ($LASTEXITCODE -ne 0) {
        throw "Claude 執行失敗，離開代碼為 $LASTEXITCODE"
    }
    Write-Output "執行紀錄已寫入: $RunLog"
}
catch {
    $ErrMsg = $_.ToString()
    Write-Output "偵測到異常，正在發送 LINE 警報：$ErrMsg"
    
    # 呼叫 Python 發送警報至 LINE
    & .venv/Scripts/python.exe tools/send_alert.py "偵測到執行異常！`n原因：$ErrMsg`n`n請確認 Chrome 瀏覽器已開啟，且 Claude Code 擴充功能已成功連線！"
}
