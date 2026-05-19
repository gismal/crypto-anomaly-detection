# 🟢🔴 Real-Time Crypto Anomaly Detection Pipeline

This project is a real-time machine learning pipeline that streams live Bitcoin (BTC/USDT) trades from Binance, engineers statistical features on the fly, and detects market anomalies using Unsupervised Machine Learning. 

It is designed with strict **Object-Oriented Programming (OOP)** principles and includes robust pipeline mechanics like rate-limiting, dynamic model retraining, and real-time Discord alerting.

---

## 🏗️ System Architecture (OOP Design)
The project is divided into highly cohesive, loosely coupled modules:

* **`BinanceStreamer` (Data Ingestion):** Runs on a background thread using WebSockets to pull live tick-level data without blocking the main event loop. Uses a `Queue` for thread-safe data transfer.
* **`FeatureEngine` (Data Engineering):** Maintains a rolling 60-second time-series window. Transforms raw prices into meaningful statistical vectors.
* **`AnomalyDetector` (Machine Learning):** Wraps the `scikit-learn` Isolation Forest model. Handles the initial warmup phase, prediction, and periodic retraining.
* **`DiscordNotifier` (Alerting):** Formats and dispatches critical anomaly alerts and periodic system health checks via Discord Webhooks.

---

## 📊 Feature Engineering (Statistical Extraction)
Raw price data is not enough for an ML model to understand market context. The `FeatureEngine` calculates the following features in real-time over a sliding window:

* **Rolling Mean & Standard Deviation:** Establishes the baseline normal behavior for the last minute.
* **Z-Score:** Measures how many standard deviations the current price is away from the rolling mean. *Crucial for detecting sudden spikes or crashes.*
* **Percentage Change (pct_change):** Captures the velocity of the price movement.
* **High-Low Spread:** Measures the volatility and amplitude within the current window.
* **Price Change:** The absolute dollar difference from the previous tick.

---

## 🧠 Machine Learning (Isolation Forest)
We utilize **Isolation Forest**, an unsupervised anomaly detection algorithm, to find needles in the haystack.

* **Warmup Period:** The bot silently observes the first 60 ticks to build an initial baseline matrix before making any predictions.
* **Contamination Tuning:** Tuned to `0.0001` to ignore micro-fluctuations and only trigger on severe, statistically significant market breakdowns.
* **Concept Drift Management:** Crypto markets are highly dynamic. The model automatically **retrains itself** periodically using a sliding buffer of the most recent market data to adapt to new "normal" price levels.
* **Explainable AI (XAI):** When an anomaly is detected, the model calculates which specific feature (e.g., *Z-Score* or *High-Low Spread*) deviated the most to explain *why* it triggered the alert.

---

## ⚙️ Core Pipeline Mechanics

* **Rate Limiting (Speed Bumps):** Binance WebSockets can send up to 30 ticks per second. A built-in rate limiter ensures we process exactly 1 tick per second. This prevents "micro-volatility" from destroying the standard deviation and causing false positives.
* **System Heartbeat:** In quiet markets, a lack of alerts can look like a system failure. The pipeline includes a heartbeat mechanism that sends a "🟢 System Active" ping to Discord every 50 ticks to confirm the bot is healthy and processing data.
* **Graceful Logging:** All anomalies are persisted locally to an `anomalies.csv` file for historical backtesting and analysis.

---

## 🚀 Installation & Usage

### 1. Clone the repository and create a virtual environment
```bash
git clone https://github.com/yourusername/crypto-anomaly-detection.git
cd crypto-anomaly-detection
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
Ensure you have the required packages installed:
```bash
pip install scikit-learn websocket-client requests numpy pytest
```

### 3. Set up Discord Integration (Optional)
Export your webhook URL to receive live alerts:
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
```

### 4. Run the Pipeline
```bash
PYTHONPATH=. python src/pipeline.py
```

*Note: Upon startup, the bot will display "Pipeline has been initiated..." and will silently collect data for the first 60 seconds (Warmup Phase) before outputting normal/anomaly predictions.*
