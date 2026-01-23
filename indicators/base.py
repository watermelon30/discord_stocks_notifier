from abc import ABC, abstractmethod
import pandas as pd

class Indicator(ABC):
    @abstractmethod
    def calculate(self, series: pd.Series) -> pd.Series:
        """Calculate the indicator for the given series."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the display name of the indicator."""
        pass
