import streamlit as st
import pandas as pd
import time
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
    
 # placeholders for live layout
chart_placeholder = st.empty()
table_placeholder = st.empty()
    
    
# infinite loop for live updates
while True:
    df = load_data()
        
    if not df.empty:
        # get the last 100 records for visuals
        recent_df = df.tail(100)
            
        with chart_placeholder.container():
            st.subheader("Anomaly Price Chart")    
            # line chart: X axis is time, Y axis is price
            chart_data = recent_df.set_index("timestamp")["price"]
            st.line_chart(chart_data)
            
        with table_placeholder.container():
            st.subheader("Recent Anomalies")
            display_df = recent_df.sort_values(by="timestamp", ascending= False)
            st.dataframe(display_df, use_container_width= True)
            
    else:
        st.info("No anomalies recorded yet. Waiting for the bot to find some...")
        
    # Wait 5 seconds, then refresh the page
    time.sleep(5)
    st.rerun()