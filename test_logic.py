import pandas as pd
from indicators.momentum import RSIIndicator, RCIIndicator
from indicators.trend import EMAIndicator
from data.fetcher import fetch_stock_data
import sys

def test_logic():
    tickers = ["AAPL", "MSFT"]
    print(f"Fetching data for {tickers}...")
    try:
        data = fetch_stock_data(tickers)
        if data.empty:
            print("No data returned.")
            return

        print("Data fetched successfully.")
        
        for ticker in tickers:
            print(f"\nTesting {ticker}:")
            # Handle multi-index or single level
            if isinstance(data.columns, pd.MultiIndex):
                # This assumes yfinance's multi-level structure: (PriceType, Ticker) or (Ticker, PriceType)
                # Recent yfinance often does (Ticker, PriceType)
                # Let's try to access it safely
                try:
                    df = data[ticker]
                except KeyError:
                    print(f"Could not key into {ticker}")
                    continue
            else:
                df = data

            close = df['Close']
            
            # RSI
            rsi = RSIIndicator().calculate(close)
            print(f"Latest RSI: {rsi.iloc[-1]:.2f}")
            
            # RCI
            rci = RCIIndicator().calculate(close)
            print(f"Latest RCI: {rci.iloc[-1]:.2f}")
            
            # EMA
            ema200 = EMAIndicator(200).calculate(close)
            print(f"Latest EMA 200: {ema200.iloc[-1]:.2f}")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logic()
