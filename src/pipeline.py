""" Future Improvement plan:
    1. Multiplethreading
    2. Graceful Shutdown
"""

import time
from src.data_ingestion import BinanceStreamer
from src.feature_engine import FeatureEngine
from src.model import AnomalyDetector
from src.alerts import CSVLogger, DiscordNotifier
from src.config import logger

def main():
    """"
    Initialized all components and runs the main event loop
    Continuously fetches price data, computes the features, predicts anomalies and dispatches alerts to Discords
    """
    logger.info("Pipeline has been intiated...")
    
    streamer = BinanceStreamer()
    engine = FeatureEngine(window_size=60) 
    model = AnomalyDetector(warmup_period= 60 , contamination= 0.0001)
    
    csv_logger = CSVLogger()
    notifier = DiscordNotifier()
    
    # Heartbeat signal to monitor the system if it is too quite for a long time
    processed_ticks = 0
    HEARTBEAT_INTERVAL = 50
    
    last_process_time = 0
    
    try:
        while True:
            data = streamer.get_next()
            if not data or data.get("price") is None:
                time.sleep(0.01)
                continue
            
            current_time = time.time()
            if current_time - last_process_time < 1.0:
                continue
            
            last_process_time = current_time
            
            price = data.get("price")
            processed_ticks += 1
         
            engine.update_window(price)
            features = engine.get_current_features()
            
            if not features:
                continue
            
            pred, score, reason = model.train_or_predict(features)
            
            if pred == 1:
                print(f"🟢 [NORMAL] Price: {price:.2f} | Score: {score:.3f}")
            else:
                print(f"🔴 [ANOMALy] Price: {price:.2f} | Reason: {reason} | Score: {score:.3f}")
                csv_logger.log(price, score, reason, features)
                notifier.send_alert(price, reason, score)
             
            # trigger the heartbeat 
            if processed_ticks % HEARTBEAT_INTERVAL ==  0:
                notifier.send_heartbeat(processed_ticks)
                    
    except KeyboardInterrupt:
        logger.info("Pipeline stops...")
    finally:
        streamer.stop()

if __name__ == "__main__":
    main()
            
            