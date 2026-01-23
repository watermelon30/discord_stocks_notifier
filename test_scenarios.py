
import pandas as pd
from indicators.momentum import RSIIndicator
from data.fetcher import fetch_stock_data

def test_single_ticker():
    print("\n--- Testing Single Ticker ---")
    tickers = ["AAPL"]
    data = fetch_stock_data(tickers)
    print("Columns:", data.columns)
    if 'Close' in data.columns:
        print("Success: 'Close' column found for single ticker.")
    else:
        print("FAIL: 'Close' column missing for single ticker.")

def test_invalid_ticker():
    print("\n--- Testing Invalid Ticker ---")
    tickers = ["INVALID_TICKER_XYZ"]
    data = fetch_stock_data(tickers)
    print("Data empty?", data.empty)
    print("Columns:", data.columns)

def test_mixed_valid_invalid():
    print("\n--- Testing Mixed Valid/Invalid ---")
    tickers = ["AAPL", "INVALID_XYZ"]
    data = fetch_stock_data(tickers)
    print("Columns:", data.columns)
    # Check if we can access AAPL
    if isinstance(data.columns, pd.MultiIndex):
        try:
            aapl = data["AAPL"]
            print("AAPL found in mixed result.")
        except KeyError:
            print("FAIL: AAPL not found in mixed result.")
    else:
        print("Not MultiIndex, manual check needed.")

if __name__ == "__main__":
    test_single_ticker()
    test_invalid_ticker()
    test_mixed_valid_invalid()
