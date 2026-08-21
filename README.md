# fetch-stock

自動抓取股票歷史股價資料、計算基本技術指標，並繪製走勢圖的小工具。使用 [yfinance](https://pypi.org/project/yfinance/) 取得資料、`pandas` 處理與合併資料、`matplotlib` 輸出圖表，可搭配 GitHub Actions 定期排程執行，適合作為股價追蹤。

## 功能特色

-  **抓取股價資料**：支援台股（加 `.TW`）與美股代號，可一次抓多支股票
-  **增量合併**：每次執行會與既有 CSV 合併、依日期去除重複，只保留最新一筆
-  **基本技術指標**：自動計算漲跌幅（`Change(%)`）與 5 日均線（`MA5`）
-  **走勢圖輸出**：讀取 CSV 畫出收盤價 + 5 日均線圖，下方附漲跌幅長條圖，輸出成 PNG
-  **推播通知**：讀取最新股價資料，透過 Discord Webhook 與 LINE Messaging API 推播更新通知
-  **可排程自動化**：搭配 `.github/workflows` 可在 GitHub Actions 上定期自動抓取及通知

## 專案結構

```
fetch-stock/
├── fetch_stock_general.py   # 通用版抓取腳本，可用 --tickers 指定任意股票
├── fetch_stock_tsmc.py      # 台積電 (2330.TW) 專用抓取腳本
├── plot_stock.py            # 讀取 CSV 並畫出股價走勢圖
├── stock-data/               # 抓取結果存放處（每支股票一個 CSV）
├── notify/                  # 股價通知相關腳本
│   └── notify.py            # 讀取最新股價，推播通知到 Discord 與 LINE
├── charts/                   # 產生的走勢圖 PNG
├── prompt/                   # 詢問 AI 意見的 prompt 建議
└── .github/workflows/        # GitHub Actions 自動排程設定
```

## 安裝

```bash
git clone https://github.com/tim32142000/fetch-stock.git
cd fetch-stock
pip install yfinance pandas matplotlib
```

## 使用方式

### 1. 抓取股價資料

用預設清單（台積電 2330.TW）：

```bash
python fetch_stock_general.py
```

指定單一或多支股票（代號可用逗號或空格分隔）：

```bash
python fetch_stock_general.py --tickers 2330.TW
python fetch_stock_general.py --tickers 2330.TW,2317.TW,AAPL
python fetch_stock_general.py --tickers 2330.TW 2317.TW AAPL
```

調整抓取的時間區間 / 頻率：

```bash
python fetch_stock_general.py --tickers 2330.TW --period 1mo --interval 1d
```

代號參考：
- 台股：代號後面加 `.TW`（例如台積電 `2330.TW`、鴻海 `2317.TW`）
- 美股：直接用代號（例如蘋果 `AAPL`、特斯拉 `TSLA`）

也可以只執行台積電專用腳本：

```bash
python fetch_stock_tsmc.py
```

抓取結果會存到 `stock-data/<代號>.csv`（例如 `stock-data/2330_TW.csv`），每次執行會覆蓋更新同一份主檔案。

### 2. 畫出走勢圖

```bash
python plot_stock.py --ticker 2330.TW
```

只顯示最近 N 筆資料：

```bash
python plot_stock.py --ticker 2330.TW --last-n 30
```

圖表會輸出到 `charts/<代號>_<日期>.png`。

### 3. 發送通知
```bash
python notify/notify.py
```

會讀取 `stock-data/` 底下最新的股價資料，透過 Discord Webhook 與 LINE Messaging API 推播更新通知。執行前請先設定好對應的金鑰／Webhook URL（建議透過環境變數或 GitHub Actions Secrets 管理，不要直接寫死在程式碼裡）。

## 自動化排程

`.github/workflows` 中設有 GitHub Actions 設定，可依排程自動執行抓取（及/或繪圖）腳本，並將更新後的資料提交回儲存庫，不需手動執行。

