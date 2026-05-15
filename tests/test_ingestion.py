import time
from src.data_ingestion import BinanceStreamer
from src.config import logger

def run_test():
    # init the streamer
    streamer = BinanceStreamer()
    
    logger.info("Connectiong to Binance...")
    streamer.connect()
    
    logger.log(" ----- Live Data (10 Secs) -------")
    start_time = time.time()
    
    try:
        while time.time() - start_time < 10:
            datapoint = streamer.get_next_tick()
            
            if datapoint:
                logger.log(f"Data Received: {datapoint}")
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    finally:
        streamer.close()
        logger.log("------ Test Completed -------")
            
if __name__ == "__main__":
    run_test()    
        