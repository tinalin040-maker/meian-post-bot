"""在 logs/daily_post.log 附加一行帶時間戳的紀錄。

用法：
    python tools/log_result.py "成功 | 划算商品: 陳家汕頭意麵$600, 每日一物松葉蟹$1799 | 獨家品牌: OPC-3 雙層Q心嚼粒 NT$1300"
"""

import sys
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "daily_post.log"


def main():
    if len(sys.argv) != 2:
        print("用法: python tools/log_result.py \"<訊息>\"", file=sys.stderr)
        sys.exit(1)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {sys.argv[1]}\n")


if __name__ == "__main__":
    main()
