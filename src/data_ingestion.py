from abc import ABC, abstractmethod
import json 
from typing import Dict, Any, Optional
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager
from src.config import logger, SYMBOL

class DataStreamer(ABC):
    """
    Abstract Base Class for all data streaming sources
    ABC applied for possible future extensions (new markets etc. )
    This interface ensures that any new exchange added to the system implements the necesarry methods for the pipeline to functions
    """
    @abstractmethod
    def connect(self) -> None:
        """ Establishes connection to the data source """
        pass
    
    @abstractmethod
    def get_next(self) -> Optional[Dict[str, Any]]:
        """ Retrieves the next processed data point """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """ Safely terminates the connection """
        
class BinanceStreamer(DataStreamer):
    """
    Binance specific implementation of the DataStreamer
    
    Uses high performance WebSocket bia unicorn-binance-websocket-api
    """
    
    def __init__(self, symbol: str = SYMBOL):
        self.symbol = symbol
        self.manager = None
        
    def connect(self) -> None:
        try:
            self.manager = BinanceWebSocketApiManager(exchange= "binance.com")
            self.manager.create_stream(["ticker"], [self.symbol])
            logger.info(f"Binance WebSocket connected for {self.symbol.upper()}.")
        except Exception as e:
            logger.error(f"Binance connection error: {e}")
            
    def get_next(self) -> Optional[Dict[str, Any]]:
        if not self.manager:
            return None
        
        raw_data = self.manager.pop_stream_data_from_stream_buffer()
        
        if raw_data:
            data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            
            # Standardization: always return the same structure
            if 'data' in data and 'c' in data['data']:
                return {
                    "time": int(data['data']['E']),
                    "price": float(data['data']['c'])
                }  
        return None
    
    def close(self) -> None:
        if self.manager:
            self.manager.stop_manager_with_all_streams()
            logger.info("Binance connection closed")
    