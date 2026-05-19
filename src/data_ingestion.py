import json
import websocket
import threading
from queue import Queue
from src.config import logger

class BinanceStreamer:
    """
    Connect to the Binance WebSocket API to stream live trade data
    Runs in a background thread to prevent blocking the main pipeline
    """
    def __init__(self, symbol="btcusdt"):
        """
        Initializes the Binance Streamer
        Args:
            - symbol (str): The trading pair symbol to stream (default is "btcusdt)
        
        """
        
        self.symbol = symbol
        self.url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"
        self.queue = Queue(maxsize=100)
        self.ws = None
        
        # Another thread to not interrupt the main stream
        self.thread = threading.Thread(target=self._start_ws)
        self.thread.daemon = True
        self.thread.start()

    def _on_message(self, ws, message):
        """
        Callback function for incoming WebSocket messages
        Parses the JSON payload and puts the price data into the queue
        """
        try:
            data = json.loads(message)
            if 'p' in data:  
                self.queue.put({"price": float(data['p'])})
        except Exception as e:
            logger.error(f"Veri ayrıştırma hatası: {e}")

    def _on_error(self, ws, error):
        """ Callback function to handle and log WebSocket errors """
        logger.error(f"WebSocket Error: {error}")

    def _start_ws(self):
        """ Internal method to run the WebSocket conncection indefinetely """
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self._on_message,
            on_error=self._on_error
        )
        self.ws.run_forever()

    def get_next(self):
        """ 
        Retries the next available price tick from the queue
        
        Returns:
            - dict: A dictionary containing the price or None if the queue is empty
        """
        if not self.queue.empty():
            return self.queue.get()
        return None

    def stop(self):
        """ Closes the WebSocket connection and stops the background thread gracefully"""
        if self.ws:
            self.ws.close()