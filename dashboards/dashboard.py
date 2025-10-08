import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Event

st.set_page_config(page_title="CyberCyte - Home", layout="wide")

st.image("images/cybercyte_logo.png", width=750)
st.title("🛡️ CyberCyte: Autonomous Home Defense System")
st.subheader("Welcome to CyberCyte")
st.write("CyberCyte is an autonomous home defense system. Navigate using the sidebar.")

# Load events from database
def get_events_from_db(limit=50):
    db: Session = SessionLocal()
    try:
        return db.query(Event).order_by(Event.id.desc()).limit(limit).all()
    finally:
        db.close()

events = get_events_from_db()
df = pd.DataFrame([{
    "src_ip": e.src_ip,
    "dst_ip": e.dst_ip,
    "src_port": e.src_port,
    "dst_port": e.dst_port,
    "protocol": e.protocol,
    "severity": e.severity,
    "description": e.description,
    "created_at": e.created_at
} for e in events])

st.subheader("Recent Events")
st.dataframe(df)
import streamlit as st

st.title("About CyberCyte")

st.write("""
CyberCyte is a student-built **autonomous cyber defense project**.  
It integrates data collection, anomaly detection, and real-time dashboards to simulate home defense.
""")

st.subheader("Team")
st.markdown("""
- Data Collector Engineer  - Ashley Saunders
- Detector & Model Engineer - Theodora Ikeri
- API & Backend Developer - Zion Auguste
- Dashboard Developer - AuJanai Horton
- Agent & osquery Integrator - Bryson Faust
- Deployment & Lab Engineer - Mikala Mitchell
""")

st.info("Built for educational purposes, not for production deployment.")
