from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .database import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    name = Column(String, index=True)
    severity = Column(String, default="medium")
    details = Column(JSON, nullable=True)
    mitigated = Column(Integer, default=0)


class RawLog(Base):
    __tablename__ = "raw_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    host_id = Column(String)
    src_ip = Column(String)
    dst_ip = Column(String)
    event_type = Column(String)
    event_text = Column(String)
    bytes_sent = Column(Integer, default=0)
    bytes_received = Column(Integer, default=0)
    processed = Column(Integer, default=0)
