import pandas as pd 
import json
import os
from src.config import logger
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
        
    def get_current_features(self) -> Optional[Dict[str, float]]:
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
            "z_score": float((self.price_history[-1] - series.mean()) / (series.std() + 1e-8)),
            "pct_change": float(((self.price_history[-1] - self.price_history[0]) / self.price_history[0]) * 100),
            "high_low_spread": float(max(self.price_history) - min(self.price_history))
        }
        
    def save_state(self, file_path = "state.json"):
        """ Converts the info on RAM into deque and saves as JSON """
        try:
            state_data = {
                "price_history": list(self.price_history)
            }
            
            with open(file_path, "w") as f:
                json.dump(state_data, f)
            logger.info(f"State has been saved: {len(self.price_history)} data")
        except Exception as e:
            logger.error(f"Error while saving: {e}")
            
    
    def load_state(self, file_path= "state.json"):
        """ Loads the JSON file back to the memo"""
        if not os.path.exists(file_path):
            logger.info("No state data, starting over")
            return
        
        try:
            with open(file_path, "r") as f:
                state_data = json.load(f)
                
                saved_history = state_data.get("price_history", [])
                for price in saved_history:
                    self.price_history.append(price)
                    
                logger.info(f"State has been loaded: {len(self.price_history)} data")
        except Exception as e:
            logger.error(f"Error while loading: {e}")
        