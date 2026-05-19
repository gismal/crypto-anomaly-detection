import pandas as pd 
from collections import deque
from typing import Dict, Optional
from src.config import WINDOW_SIZE

class FeatureEngine:
    """ Processes raw price data into statistical feature """
    def __init__(self, window_size: int = WINDOW_SIZE):
        self.window_size = window_size
        self.price_history = deque(maxlen = window_size)
        
    def update_window(self, price: float) -> None:
        self.price_history.append(price)
        
    def get_current_feature(self) -> Optional[Dict[str, float]]:
        """
        Calculates statistical and financial features based on the current price window
        
        Features included:
            - current_price: The most recent price in the window
            - rolling_mean: Average price over the window
            - rolling_std: Price volatility, standard deviation (std)
            - price_change: Absolute difference between the first and last price
            - z_score: How many stds the current price is from the mean
            - pct_change: Percentage growth or decline from the start of the window
            - high_low_spread: The gap between the absolute highest and loewst prices
            
        """
        
        if len(self.price_history) < self.window_size:
            return None
        
        series = pd.Series(list(self.price_history))
    
        return {
            "current_price": float(self.price_history[-1]),
            "rolling_mean": float(series.mean()),
            "rolling_std": float(series.std()),
            "price_change": float(self.price_history[-1] - self.price_history[0]),
            "z_score": float((self.price_history[-1] - series.mean()) / (series.mean()) / (series.std() + 1e-8)),
            "pct_change": float(((self.price_history[-1] - self.price_history[0]) / self.price_history[0]) * 100),
            "high_low_spread": float(max(self.price_history) - min(self.price_history))
        }