# 由 Windows 工作排程器每天 09:00 觸發。
# 前置需求：這台電腦的 Chrome 必須已開啟並登入 shop.com，Claude Code 的 Chrome 擴充功能已連線。

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

$Prompt = Get-Content -Raw -Encoding UTF8 (Join-Path $ProjectDir "skills\daily_post.md")

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

$null | claude -p $Prompt `
    --chrome `
    --allowedTools $AllowedTools `
    *> $RunLog

Write-Output "執行紀錄已寫入: $RunLog"
