import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000/events"

st.title("Live Incidents")

try:
    resp = requests.get(API_URL)
    events = pd.DataFrame(resp.json())
except:
    st.error("Failed to fetch events from API")
    events = pd.DataFrame()

if not events.empty:
    st.dataframe(events)
