"""
fetch_stock_genarl.py

自動抓取指定股票的股價資料，並合併更新到各自的主檔案（CSV）。

用法範例：
    # 用預設股票清單（台積電）
    python fetch_stock_genarl.py

    # 指定單一股票
    python fetch_stock_genarl.py --tickers 2330.TW

    # 指定多支股票（用逗號分隔，不要有空格，或用空格分隔多個參數皆可）
    python fetch_stock_genarl.py --tickers 2330.TW,2317.TW,AAPL
    python fetch_stock_genarl.py --tickers 2330.TW 2317.TW AAPL

    # 調整抓取天數區間
    python fetch_stock_genarl.py --tickers 2330.TW --period 1mo

代號參考：
    - 台股：代號後面加 .TW（例如台積電 2330.TW、鴻海 2317.TW）
    - 美股：直接用代號（例如蘋果 AAPL、特斯拉 TSLA）

需要先安裝套件：
    pip install yfinance pandas
"""

import argparse
import os

import pandas as pd
import yfinance as yf

# ------------------- 預設設定 -------------------
DEFAULT_TICKERS = ["2330.TW"]   # 沒有指定 --tickers 時，預設抓的股票清單
DATA_DIR = "data"                # 資料存放資料夾
DEFAULT_PERIOD = "5d"            # 抓最近幾天的資料（也可用 "1mo", "1y" 等）
DEFAULT_INTERVAL = "1d"          # 資料頻率：1d = 日線


def parse_args() -> argparse.Namespace:
    """解析命令列參數，決定要抓哪些股票、抓多久的區間"""
    parser = argparse.ArgumentParser(description="定期抓取股價資料並合併存檔")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=DEFAULT_TICKERS,
        help=(
            "要抓取的股票代號，可用逗號或空格分隔多支股票"
            "（例如 --tickers 2330.TW,2317.TW 或 --tickers 2330.TW 2317.TW）"
        ),
    )
    parser.add_argument(
        "--period",
        default=DEFAULT_PERIOD,
        help="抓取的時間區間，例如 5d, 1mo, 1y（預設 5d）",
    )
    parser.add_argument(
        "--interval",
        default=DEFAULT_INTERVAL,
        help="資料頻率，例如 1d, 1h（預設 1d）",
    )

    args = parser.parse_args()

    # 支援 --tickers 用逗號分隔寫在同一個字串裡的情況
    tickers = []
    for item in args.tickers:
        tickers.extend([t.strip() for t in item.split(",") if t.strip()])
    args.tickers = tickers

    return args


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
    """把資料存成單一主檔案（檔名不帶日期，每支股票各自一個檔案），每次執行覆蓋更新"""
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = os.path.join(DATA_DIR, f"{ticker.replace('.', '_')}.csv")
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    return filename


def process_ticker(ticker: str, period: str, interval: str) -> None:
    """處理單一股票：抓取 -> 合併 -> 加指標 -> 存檔 -> 印摘要"""
    print(f"\n開始抓取 {ticker} 的股價資料...")
    raw_df = fetch_stock_data(ticker, period, interval)

    filepath = os.path.join(DATA_DIR, f"{ticker.replace('.', '_')}.csv")
    merged_df = merge_with_existing(raw_df, filepath)
    df = add_basic_indicators(merged_df)

    saved_path = save_to_csv(df, ticker)
    print(f"已更新主檔案：{saved_path}（目前共 {len(df)} 筆資料）")

    latest = df.iloc[-1]
    print(f"最新日期：{latest['Date']}")
    print(f"收盤價：{latest['Close']:.2f}")
    print(f"漲跌幅：{latest['Change(%)']:.2f}%")
    print(f"5日均線：{latest['MA5']:.2f}")


def main():
    args = parse_args()

    print(f"本次要抓取的股票：{', '.join(args.tickers)}")

    # 逐支股票處理，單支失敗不影響其他股票繼續抓取
    failed = []
    for ticker in args.tickers:
        try:
            process_ticker(ticker, args.period, args.interval)
        except Exception as e:
            print(f"[錯誤] 抓取 {ticker} 失敗：{e}")
            failed.append(ticker)

    print("\n=== 執行結果 ===")
    success_count = len(args.tickers) - len(failed)
    print(f"成功：{success_count} / {len(args.tickers)}")
    if failed:
        print(f"失敗清單：{', '.join(failed)}")


if __name__ == "__main__":
    main()