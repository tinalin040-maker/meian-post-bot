# -*- coding: utf-8 -*-
import glob
import json
import gspread
import os
from datetime import datetime

# 尋找 service_account.json
paths = [f for f in glob.glob('C:/ai-agent-center/projects/**/*.json', recursive=True) if 'service_account' in f]
if not paths:
    print("找不到 service_account.json 憑證檔案")
    exit(1)

service_account_path = paths[0]
print(f"使用憑證: {service_account_path}")

# 讀取今日商品資料
json_path = r"c:\ai-agent-center\projects\美安貼文bot\output\2026-07-11.json"
with open(json_path, "r", encoding="utf-8") as f:
    items = json.load(f)

# 連線 Google Sheets
gc = gspread.service_account(filename=service_account_path)

sheet_name = "美安商品貼文紀錄"
spreadsheet = None

try:
    # 嘗試開啟現有的試算表
    spreadsheet = gc.open(sheet_name)
    print("已成功開啟現有試算表。")
except gspread.exceptions.SpreadsheetNotFound:
    # 引導使用者手動建立與共用
    print("\n[IMPORTANT] 找不到試算表！請在您的 Google Drive / Google Sheets 手動建立一個名為「美安商品貼文紀錄」的試算表，並共用編輯權限給以下服務帳號信箱：")
    print("  relin-invoice-bot@relin-invoice-automation.iam.gserviceaccount.com")
    print("共用完成後，請重新執行此腳本即可自動寫入！\n")
    exit(1)

worksheet = spreadsheet.get_worksheet(0)

# 如果是新表，寫入表頭
if worksheet.row_count == 1 and worksheet.cell(1, 1).value == "":
    worksheet.append_row(["日期", "商品名稱", "原價", "優惠特價", "原始網址"])

# 準備寫入資料
today_str = datetime.now().strftime("%Y-%m-%d")
rows_written = 0

for item in items:
    # 獲取商品連結 (相容 link 與 url)
    link = item.get("link") or item.get("url") or ""
    
    # 檢查是否已存在今日該商品的紀錄，防止重複寫入
    cell_list = worksheet.findall(item["name"])
    already_exists = False
    for cell in cell_list:
        row_vals = worksheet.row_values(cell.row)
        if len(row_vals) > 0 and row_vals[0] == today_str:
            already_exists = True
            break
            
    if not already_exists:
        worksheet.append_row([
            today_str,
            item["name"],
            item.get("price_original", ""),
            item.get("price_sale", ""),
            link
        ])
        rows_written += 1

print(f"成功寫入 {rows_written} 筆商品紀錄。")
print(f"試算表網址: {spreadsheet.url}")
