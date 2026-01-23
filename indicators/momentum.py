import pandas as pd
import numpy as np
from .base import Indicator

class RSIIndicator(Indicator):
    def __init__(self, period=14, low_threshold=25):
        self.period = period
        self.low_threshold = low_threshold

    @property
    def name(self) -> str:
        return f"RSI ({self.period})"

    def calculate(self, series: pd.Series) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Use classic Wilder's smoothing if preferred, but simple rolling is efficiently close for this purpose
        # For more accuracy with Wilder's:
        # gain = delta.where(delta > 0, 0)
        # loss = -delta.where(delta < 0, 0)
        # avg_gain = gain.ewm(alpha=1/self.period, adjust=False).mean()
        # avg_loss = loss.ewm(alpha=1/self.period, adjust=False).mean()
        # rs = avg_gain / avg_loss
        # rsi = 100 - (100 / (1 + rs))
        
        # Using Wilder's smoothing as it is standard for RSI
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(com=self.period - 1, min_periods=self.period).mean()
        avg_loss = loss.ewm(com=self.period - 1, min_periods=self.period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

class RCIIndicator(Indicator):
    def __init__(self, period=9, low_threshold=-80):
        self.period = period
        self.low_threshold = low_threshold

    @property
    def name(self) -> str:
        return f"RCI ({self.period})"
    
    def calculate(self, series: pd.Series) -> pd.Series:
        # RCI is Rank Correlation Index (Spearman correlation with time)
        # We need a rolling Spearman correlation
        
        def rolling_spearman(slice_series):
            n = len(slice_series)
            time_rank = np.arange(1, n + 1)
            price_rank = slice_series.rank().values
            
            d_sq = np.sum((time_rank - price_rank) ** 2)
            rci = (1 - (6 * d_sq) / (n * (n**2 - 1))) * 100
            return rci

        # Rolling apply is slow, but RCI is typically done on small window (9)
        return series.rolling(window=self.period).apply(rolling_spearman, raw=False)
