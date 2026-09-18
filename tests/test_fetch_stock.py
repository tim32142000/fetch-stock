import sys
import types
import unittest
from unittest.mock import patch

import pandas as pd

# 測試只需確認傳給 yfinance 的參數，不必連線或安裝 yfinance。
fake_yfinance = types.ModuleType("yfinance")
fake_yfinance.Ticker = None
sys.modules.setdefault("yfinance", fake_yfinance)

import fetch_stock_general
import fetch_stock_tsmc


class FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.history_kwargs = None

    def history(self, **kwargs):
        self.history_kwargs = kwargs
        return pd.DataFrame(
            {
                "Open": [2445.0000000001],
                "High": [2455.0000000001],
                "Low": [2434.9999999999],
                "Close": [2450.0000000001],
                "Adj Close": [2442.809326171875],
                "Volume": [17_578_157],
                "Dividends": [0.0],
                "Stock Splits": [0.0],
            },
            index=pd.DatetimeIndex(["2026-09-10"], name="Date"),
        )


class FetchStockDataTests(unittest.TestCase):
    def test_fetchers_keep_unadjusted_ohlc_and_round_only_prices(self):
        for module in (fetch_stock_general, fetch_stock_tsmc):
            with self.subTest(module=module.__name__):
                fake_ticker = FakeTicker("2330.TW")
                with patch.object(module.yf, "Ticker", return_value=fake_ticker):
                    result = module.fetch_stock_data("2330.TW", "5d", "1d")

                self.assertFalse(fake_ticker.history_kwargs["auto_adjust"])
                self.assertEqual(
                    result.loc[0, ["Open", "High", "Low", "Close"]].tolist(),
                    [2445.0, 2455.0, 2435.0, 2450.0],
                )
                self.assertEqual(result.loc[0, "Volume"], 17_578_157)
                self.assertNotIn("Adj Close", result.columns)


if __name__ == "__main__":
    unittest.main()
