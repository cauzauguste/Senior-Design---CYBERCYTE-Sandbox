# threat_manager.py
import asyncio
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Event
from app.osquery_agent import get_osquery_events  # your osquery collector
from app.zeek_parser import parse_zeek_logs     # your zeek parser

# For anomaly detection
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.preprocessing import StandardScaler

from app.database import get_db
from app.models import RawLog
from datetime import datetime

def log_threat_to_db(host_id: str, src_ip: str, event_type: str, event_text: str, db_session=None):
    """
    Logs a detected threat to the database.
    """
    db = db_session or get_db()
    new_event = RawLog(
        host_id=host_id,
        src_ip=src_ip,
        event_type=event_type,
        event_text=event_text,
        bytes_sent=0,
        bytes_received=0,
        timestamp=datetime.utcnow(),
        processed=1  # mark as processed
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

# -------------------------
# Database helpers
# -------------------------
def insert_event(db: Session, event_data: Dict[str, Any]):
    db_event = Event(
        src_ip=event_data.get('src_ip', ''),
        dst_ip=event_data.get('dst_ip', ''),
        src_port=event_data.get('src_port', 0),
        dst_port=event_data.get('dst_port', 0),
        protocol=event_data.get('protocol', ''),
        severity=event_data.get('severity', 'medium'),
        description=event_data.get('description', None),
        created_at=event_data.get('created_at', datetime.utcnow())
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# -------------------------
# Threat Models
# -------------------------
class SimpleIsolationForestModel:
    def __init__(self, contamination=0.05):
        self.model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
        X = np.array([[100, 200], [120, 220], [90, 180]])
        self.scaler = StandardScaler().fit(X)
        self.model.fit(self.scaler.transform(X))

    def predict(self, features: Dict[str, Any]):
        x = np.array([[features.get('bytes_sent', 0), features.get('bytes_received', 0)]])
        x_scaled = self.scaler.transform(x)
        pred = self.model.predict(x_scaled)
        score = self.model.decision_function(x_scaled)[0]
        return {'anomaly': bool(pred[0] == -1), 'score': float(score)}


class SimpleRandomForestNetModel:
    def __init__(self):
        X = np.array([[200, 300, 1], [40000, 10, 0.2], [500, 600, 2]])
        y = np.array([0, 1, 0])
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        self.model.fit(X, y)

    def predict(self, features: Dict[str, Any]):
        x = np.array([[features.get('bytes_sent', 0), features.get('bytes_received', 0), features.get('duration', 1)]])
        pred = self.model.predict(x)[0]
        prob = self.model.predict_proba(x).tolist()[0] if hasattr(self.model, 'predict_proba') else [0.0, 1.0]
        return {'attack': bool(pred == 1), 'prob': prob}


class EmberLikeMalwareModel:
    def __init__(self):
        X = np.array([[120000, 30], [20000, 200], [5000000, 5]])
        y = np.array([0, 0, 1])
        self.model = LGBMClassifier()
        self.model.fit(X, y)

    def predict(self, features: Dict[str, Any]):
        x = np.array([[features.get('file_size', 0), features.get('num_imports', 0)]])
        pred = int(self.model.predict(x)[0])
        return {'malware': bool(pred == 1)}


class DeepLogLike:
    def predict(self, sequence: List[str]):
        forbidden = ['rm -rf /', 'mimikatz', 'suspicious-lateral']
        for token in forbidden:
            if token in " ".join(sequence).lower():
                return {'anomaly': True, 'reason': token}
        return {'anomaly': False}


class LogBERTLike:
    def predict(self, text: str):
        suspicious_keywords = ['encoded', 'obfuscat', 'powershell', 'base64']
        for kw in suspicious_keywords:
            if kw in text.lower():
                return {'anomaly': True, 'keyword': kw}
        return {'anomaly': False}


# -------------------------
# Threat Manager
# -------------------------
class ThreatManager:
    def __init__(self, models: Dict[str, Any]):
        self.models = models
        self.running = False

    async def pull_and_run(self):
        db: Session = SessionLocal()
        try:
            # Collect events from osquery
            osquery_events = get_osquery_events()
            for ev in osquery_events:
                insert_event(db, ev)

            # Collect events from Zeek logs
            zeek_events = parse_zeek_logs()
            for ev in zeek_events:
                insert_event(db, ev)

            # Run models on recent events
            recent_events = db.query(Event).order_by(Event.created_at.desc()).limit(50).all()
            for ev in recent_events:
                features = {
                    'bytes_sent': getattr(ev, 'bytes_sent', 0),
                    'bytes_received': getattr(ev, 'bytes_received', 0),
                    'duration': 1,
                    'file_size': getattr(ev, 'file_size', 0),
                    'num_imports': getattr(ev, 'num_imports', 0)
                }

                if 'iforest' in self.models:
                    out = self.models['iforest'].predict(features)
                    if out['anomaly']:
                        ev.severity = 'medium'
                        ev.description = f"IsolationForest anomaly, score: {out['score']}"
                        db.commit()

                if 'netrf' in self.models:
                    out = self.models['netrf'].predict(features)
                    if out.get('attack'):
                        ev.severity = 'high'
                        ev.description = f"Network Attack, prob: {out.get('prob')}"
                        db.commit()

                if 'ember' in self.models and getattr(ev, 'file_size', None):
                    out = self.models['ember'].predict(features)
                    if out['malware']:
                        ev.severity = 'critical'
                        ev.description = "Malware detected (Ember-like)"
                        db.commit()

                if 'deeplog' in self.models:
                    seq = getattr(ev, 'description', '').split('|')
                    out = self.models['deeplog'].predict(seq)
                    if out['anomaly']:
                        ev.severity = 'high'
                        ev.description += f" | DeepLog anomaly: {out.get('reason')}"
                        db.commit()

                if 'logbert' in self.models:
                    out = self.models['logbert'].predict(getattr(ev, 'description', ''))
                    if out['anomaly']:
                        ev.severity = 'high'
                        ev.description += f" | LogBERT anomaly: {out.get('keyword')}"
                        db.commit()

        finally:
            db.close()

    async def run_loop(self, interval_seconds=10):
        self.running = True
        while self.running:
            try:
                await self.pull_and_run()
            except Exception as e:
                print("Error in ThreatManager loop:", e)
            await asyncio.sleep(interval_seconds)

    def stop(self):
        self.running = False
