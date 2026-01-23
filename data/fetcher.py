import yfinance as yf
import pandas as pd

def fetch_stock_data(tickers: list[str], period="2y") -> pd.DataFrame:
    """
    Fetch stock data for given tickers.
    Returns specific 'Close' price mostly related.
    
    If multiple tickers, yf returns MultiIndex columns.
    We generally want just the Close prices for this app.
    """
    if not tickers:
        return pd.DataFrame()
        
    data = yf.download(tickers, period=period, group_by='ticker', auto_adjust=True)
    
    # If single ticker, structure is simpler
    # If single ticker, structure is simpler
    # But yfinance consistently returns MultiIndex with the current settings if multiple tickers are possible 
    # or sometimes flat. The app logic should handle the structure.
    return data

def get_latest_price(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return series.iloc[-1]
