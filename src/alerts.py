import requests
import csv 
import os 
from datetime import datetime
from src.config import logger

class CSVLogger:
    """ Logs detected anomalies and their features to a CSV file for future ML training"""
    def __init__(self, filename: str = "anomalies.csv"):
        self.filename = filename
        self.headers = [
            "timestamp", "price", "prediction_score", "reason", 
            "rolling_mean", "rolling_std", "price_change", 
            "z_score", "pct_change", "high_low_spread"
        ]
        
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                logger.info(f"Created new anomaly log file: {self.filename}")
                
    def log(self, price: float, score: float, reason: str, features: dict):
        """ Appends the anomaly event to the CSV """
        with open(self.filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                round(price, 2), round(score, 4), reason,
                round(features["rolling_mean"], 4), round(features["rolling_std"], 4),
                round(features["price_change"], 4), round(features["z_score"], 4),
                round(features["pct_change"], 4), round(features["high_low_spread"], 4)
            ])
            
class DiscordNotifier:
    """Sends real time anomaly alerts to a Discord channel via Webhook"""
    
    def __init__(self):
        # Environmental variables will be here! Empty strign for the simulation
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        # will be => self.webhook_url = "https://discord.com/api/webhooks/..."
        
    def send_alert(self, price: float, reason: str, score: float):
        """ Dispatches the alert using Discord's Rich Embed format"""
        
        
        # Embed card for Discord
        payload = {
            "username": "Crypto Anomaly Bot",
            "avatar_url" : "https://i.postimg.cc/prWBDtnN/Adsiz.png",
            "embeds": [{
                "title": "🚨 Crypto Anomaly Detected! 🚨",
                "color": 16711680,
                "fields": [
                    {"name": "💰 Price", "value": f"${price:,.2f}", "inline": True},
                    {"name": "📉 Reason", "value": f"`{reason}`", "inline": True},
                    {"name": "📊 Risk Score", "value": f"**{score:.3f}**", "inline": False}
                ],
                "footer": {"text": "Isolation Forest ML Engine"}
            }]
        }
        
        if not self.webhook_url:
            logger.info(f"[SIMULATION] Discord Embed Notification \nPrice: {price}  | Reason: {reason}")
            return
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord Error: {e}")    
        
    def send_heartbeat(self, processed_ticks: int):
        """Sends a periodic status update to ensure the bot is alive."""
        payload = {
            "username": "Crypto Anomaly Bot",
            "avatar_url": "https://i.postimg.cc/prWBDtnN/Adsiz.png",
            "embeds": [{
                "title": "🟢 Sistem Aktif (Heartbeat)",
                "color": 65280,
                "description": f"Bot sorunsuz şekilde çalışmaya devam ediyor.\n\n📊 **İşlenen Toplam Veri:** `{processed_ticks}`",
                "footer": {"text": "System Health Monitor"}
            }]
        }
        
        if not self.webhook_url:
            logger.info(f"[SIMULATION] Heartbeat Gönderildi. İşlenen Veri: {processed_ticks}")
            return
            
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Heartbeat gönderim hatası: {e}")