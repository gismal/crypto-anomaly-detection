import logging 

SYMBOL = "btcusdt"
WINDOW_SIZE = 60
CONTAMINATION = 0.01

logging.basicConfig(
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CryptoAnomaly")