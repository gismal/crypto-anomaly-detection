import logging 
import os
from dotenv import load_dotenv

#----- Project Constraint ------
SYMBOL = "btcusdt"
WINDOW_SIZE = 60  # Number of data points for feature calculation
CONTAMINATION = 0.01 # Expected percentage of anomalies  (%1)

#----- Web Hook ----------
load_dotenv() 
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

#----- Logging Configuration ----
logging.basicConfig(
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CryptoAnomaly")