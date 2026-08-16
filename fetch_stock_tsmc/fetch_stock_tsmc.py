"""
fetch_stock_tsmc.py

自動抓取台積電（TSMC）股價資料，並存成 CSV。
- 台股代號：2330.TW（台灣證交所掛牌）
- 美股 ADR 代號：TSM（如果想抓美股版本，把 TICKER 改成 "TSM" 即可）

需要先安裝套件：
    pip install yfinance pandas
"""

import os
from datetime import datetime

import pandas as pd
import yfinance as yf

# ------------------- 設定 -------------------
TICKER = "2330.TW"          # 台積電（台股）
DATA_DIR = "../stock_data"      # 資料存放資料夾
PERIOD = "5d"                # 抓最近幾天的資料（也可用 "1mo", "1y" 等）
INTERVAL = "1d"              # 資料頻率：1d = 日線


def fetch_stock_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """抓取指定股票的歷史價格資料"""
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)

    if df.empty:
        raise ValueError(f"沒有抓到 {ticker} 的資料，請確認代號是否正確或市場是否開盤")

    df = df.reset_index()
    df["Ticker"] = ticker
    return df


def merge_with_existing(new_df: pd.DataFrame, filepath: str) -> pd.DataFrame:
    """把新抓到的資料和已存在的主檔案合併，並依日期去除重複"""
    if os.path.exists(filepath):
        old_df = pd.read_csv(filepath, parse_dates=["Date"])
        combined = pd.concat([old_df, new_df], ignore_index=True)
    else:
        combined = new_df

    # 依日期去重複：同一天若抓到多次，保留最新抓到的那一筆
    combined = combined.drop_duplicates(subset=["Date"], keep="last")
    combined = combined.sort_values("Date").reset_index(drop=True)
    return combined


def add_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """加入簡單技術指標：漲跌幅、5 日均線（在合併、排序後的完整資料上重新計算，確保連續正確）"""
    df["Change(%)"] = df["Close"].pct_change() * 100
    df["MA5"] = df["Close"].rolling(window=5, min_periods=1).mean()
    return df


def save_to_csv(df: pd.DataFrame, ticker: str) -> str:
    """把資料存成單一主檔案（檔名不帶日期），每次執行覆蓋更新"""
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = os.path.join(DATA_DIR, f"{ticker.replace('.', '_')}.csv")
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    return filename


def main():
    print(f"開始抓取 {TICKER} 的股價資料...")
    raw_df = fetch_stock_data(TICKER, PERIOD, INTERVAL)

    filepath = os.path.join(DATA_DIR, f"{TICKER.replace('.', '_')}.csv")
    merged_df = merge_with_existing(raw_df, filepath)
    df = add_basic_indicators(merged_df)

    saved_path = save_to_csv(df, TICKER)
    print(f"已更新主檔案：{saved_path}（目前共 {len(df)} 筆資料）")

    # 印出最新一筆資料摘要
    latest = df.iloc[-1]
    print("\n=== 最新資料摘要 ===")
    print(f"日期：{latest['Date']}")
    print(f"收盤價：{latest['Close']:.2f}")
    print(f"漲跌幅：{latest['Change(%)']:.2f}%")
    print(f"5日均線：{latest['MA5']:.2f}")


if __name__ == "__main__":
    main()
