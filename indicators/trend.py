import pandas as pd
from .base import Indicator

class EMAIndicator(Indicator):
    def __init__(self, period=200):
        self.period = period

    @property
    def name(self) -> str:
        return f"EMA ({self.period})"
    
    def calculate(self, series: pd.Series) -> pd.Series:
        return series.ewm(span=self.period, adjust=False).mean()

class ApproachingEMAIndicator(Indicator):
    def __init__(self, period=200, threshold_percent=2.0):
        self.period = period
        self.threshold_percent = threshold_percent
        self.ema_indicator = EMAIndicator(period)

    @property
    def name(self) -> str:
        return f"Approaching EMA ({self.period})"
    
    def calculate(self, series: pd.Series) -> pd.Series:
        ema = self.ema_indicator.calculate(series)
        # Calculate percentage difference
        diff_percent = ((series - ema).abs() / ema) * 100
        # Return True if within threshold (we return series of booleans as 0/1 or just the diff for visualization)
        # But to keep consistent with "Indicator" returning a series of values, we might want to return the Distance %
        return diff_percent
