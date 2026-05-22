import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title= "Crypto Anomaly Dashboard", layout= "wide")
st.title("Live Crypto Anomaly Monitor")

CSV_FILE = "anomalies.csv"

def load_data():
    """ Reads the anomaly log file and returns it as a pandas DataFrame"""
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(CSV_FILE)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors= "coerce")
        df = df.dropna(subset= ["timestamp"])
        
        return df
    except Exception:
        # Return an empty DataFrame if something goes wrong
        return pd.DataFrame()

# This fragment updates itself every 5 secs dynamically    
@st.fragment(run_every= 5)
def live_dashboard():
    df = load_data()
    if not df.empty:
        recent_df = df.tail(100)
        latest_anomaly = df.iloc[-1]
        
        # KPI Metrics
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="Total Anomalies", value=len(df))
        kpi2.metric(label="Latest Price", value=f"${latest_anomaly['price']:.2f}")
        kpi3.metric(label="Latest Score", value=f"{latest_anomaly['prediction_score']:.4f}")
        st.markdown("---")
        
        # 2. Chart
        st.subheader("Anomaly Price Chart")
        chart_data = recent_df.set_index("timestamp")["price"]
        st.line_chart(chart_data)
        
        # 3. Table
        st.subheader("Recent Anomalies")
        display_df = recent_df.sort_values(by="timestamp", ascending=False)
        st.dataframe(display_df, width="stretch")
    else:
        st.info("No anomalies recorded yet. Waiting for the bot to find some...")

# Start the live dashboard
live_dashboard()