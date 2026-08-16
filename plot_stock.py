"""
plot_stock.py

讀取 fetch_stock.py 產生的股價 CSV 主檔案，畫出股價走勢圖（含 5 日均線），
輸出成 PNG 圖片，可用於作品集網頁儀表板或直接展示。

用法範例：
    # 用預設股票（台積電）
    python plot_stock.py

    # 指定單一股票
    python plot_stock.py --ticker 2330.TW

    # 指定要顯示最近幾筆資料（預設全部）
    python plot_stock.py --ticker 2330.TW --last-n 30

需要先安裝套件：
    pip install pandas matplotlib
"""

import argparse
import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")  # 不需要顯示視窗，直接輸出成檔案（適合在 GitHub Actions 這種無頭環境執行）

# ------------------- 預設設定 -------------------
DEFAULT_TICKER = "2330.TW"
DATA_DIR = "stock-data"
OUTPUT_DIR = "charts"


def parse_args() -> argparse.Namespace:
    """解析命令列參數，決定要畫哪支股票、顯示多少筆資料"""
    parser = argparse.ArgumentParser(description="讀取股價 CSV，畫出走勢圖並輸出 PNG")
    parser.add_argument(
        "--ticker",
        default=DEFAULT_TICKER,
        help="要繪圖的股票代號，需與 fetch_stock.py 產生的 CSV 檔名對應（預設 2330.TW）",
    )
    parser.add_argument(
        "--last-n",
        type=int,
        default=None,
        help="只顯示最近 N 筆資料（預設不限制，顯示全部歷史資料）",
    )
    return parser.parse_args()


def load_data(ticker: str) -> pd.DataFrame:
    """讀取 fetch_stock.py 產生的主檔案 CSV"""
    filepath = os.path.join(DATA_DIR, f"{ticker.replace('.', '_')}.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"找不到 {filepath}，請先執行 fetch_stock.py 抓取 {ticker} 的資料"
        )

    df = pd.read_csv(filepath, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def plot_price_chart(df: pd.DataFrame, ticker: str) -> plt.Figure:
    """畫出收盤價 + 5日均線走勢圖，下方附上漲跌幅長條圖"""
    fig, (ax_price, ax_change) = plt.subplots(
        2, 1, figsize=(10, 6), sharex=True, height_ratios=[3, 1]
    )

    # 上方：收盤價 + 5日均線
    ax_price.plot(df["Date"], df["Close"], label="Close", color="#1f77b4", linewidth=1.8)
    if "MA5" in df.columns:
        ax_price.plot(df["Date"], df["MA5"], label="MA5", color="#ff7f0e", linewidth=1.2, linestyle="--")
    ax_price.set_ylabel("Price")
    ax_price.set_title(f"{ticker} Stock Price Trend")
    ax_price.legend(loc="upper left")
    ax_price.grid(alpha=0.3)

    # 下方：每日漲跌幅長條圖，上漲紅色、下跌綠色（依台股慣例）
    if "Change(%)" in df.columns:
        colors = ["#d62728" if v >= 0 else "#2ca02c" for v in df["Change(%)"].fillna(0)]
        ax_change.bar(df["Date"], df["Change(%)"], color=colors, width=0.8)
        ax_change.set_ylabel("Change (%)")
        ax_change.axhline(0, color="black", linewidth=0.5)
        ax_change.grid(alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def main():
    args = parse_args()

    print(f"讀取 {args.ticker} 的資料...")
    df = load_data(args.ticker)

    if args.last_n is not None:
        df = df.tail(args.last_n).reset_index(drop=True)
        print(f"只顯示最近 {args.last_n} 筆資料")

    last_date_str = df["Date"].iloc[-1].strftime("%Y%m%d")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(
        OUTPUT_DIR, f"{args.ticker.replace('.', '_')}_{last_date_str}.png"
    )

    fig = plot_price_chart(df, args.ticker)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"圖表已儲存至：{output_path}")


if __name__ == "__main__":
    main()