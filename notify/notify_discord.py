"""
notify_discord.py

讀取 fetch_stock.py 產生的股價主檔案（CSV），取出最新一天的真實資料，
組成訊息文字，推送到 Discord 頻道。

用法範例：
    python notify_discord.py
    python notify_discord.py --ticker 2330.TW

需要先安裝套件：
    pip install pandas requests

需要先設定環境變數：
    DISCORD_WEBHOOK_URL
"""

import argparse
import os

import pandas as pd
import requests

DATA_DIR = "stock-data"
DEFAULT_TICKER = os.environ.get("TICKER", "2330.TW")  # 優先讀環境變數 TICKER，沒設定才 fallback 用預設值


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="讀取最新股價資料並推送到 Discord")
    parser.add_argument(
        "--ticker",
        default=DEFAULT_TICKER,
        help="要通知的股票代號，需與 fetch_stock.py 產生的 CSV 檔名對應（預設 2330.TW）",
    )
    return parser.parse_args()


def load_latest_record(ticker: str) -> pd.Series:
    """讀取股價主檔案，回傳最新一天的資料"""
    filepath = os.path.join(DATA_DIR, f"{ticker.replace('.', '_')}.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"找不到 {filepath}，請先執行 fetch_stock.py 抓取 {ticker} 的資料"
        )

    df = pd.read_csv(filepath, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    if df.empty:
        raise ValueError(f"{filepath} 是空的，沒有資料可以通知")

    return df.iloc[-1]


def build_message(ticker: str, record: pd.Series) -> str:
    """把最新一天的真實資料組成 Discord 訊息文字"""
    date_str = record["Date"].strftime("%Y-%m-%d")
    close_price = record["Close"]
    change_pct = record.get("Change(%)")
    ma5 = record.get("MA5")

    # 漲跌加上箭頭符號，一眼看出方向
    if pd.notna(change_pct):
        arrow = "🔺" if change_pct >= 0 else "🔻"
        change_str = f"{arrow} {change_pct:+.2f}%"
    else:
        change_str = "N/A"

    ma5_str = f"{ma5:.2f}" if pd.notna(ma5) else "N/A"

    message = (
        f"📈 **{ticker}** 股價更新\n"
        f"日期：{date_str}\n"
        f"收盤價：{close_price:.2f}\n"
        f"漲跌幅：{change_str}\n"
        f"5日均線：{ma5_str}"
    )
    return message


def send_to_discord(message: str) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise EnvironmentError("環境變數 DISCORD_WEBHOOK_URL 未設定")

    response = requests.post(webhook_url, json={"content": message})
    response.raise_for_status()


def main():
    args = parse_args()

    print(f"讀取 {args.ticker} 的最新資料...")
    record = load_latest_record(args.ticker)

    message = build_message(args.ticker, record)
    print("即將發送的訊息內容：")
    print(message)

    send_to_discord(message)
    print("Discord 通知已送出")


if __name__ == "__main__":
    main()
