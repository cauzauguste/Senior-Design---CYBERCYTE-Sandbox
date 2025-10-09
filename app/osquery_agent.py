# osquery_agent.py
from datetime import datetime
from app.threat_manager import log_threat_to_db

def parse_osquery_event(event: dict):
    """
    Example osquery event:
    {
        "host_id": "host123",
        "src_ip": "192.168.1.101",
        "event_type": "portscan",
        "event_text": "Detected portscan from 192.168.1.101"
    }
    """
    log_threat_to_db(
        host_id=event["host_id"],
        src_ip=event["src_ip"],
        event_type=event["event_type"],
        event_text=event["event_text"]
    )

def parse_zeek_event(event: dict):
    # similar logic
    log_threat_to_db(
        host_id=event["host_id"],
        src_ip=event["src_ip"],
        event_type=event["event_type"],
        event_text=event["event_text"]
    )

def get_osquery_events():
    """
    Simulate getting events from osquery.
    Must return a list of dicts with Event fields.
    """
    events = [
        {
            "src_ip": "192.168.1.10",
            "dst_ip": "8.8.8.8",
            "src_port": 12345,
            "dst_port": 53,
            "protocol": "UDP",
            "severity": "medium",
            "description": "DNS query detected",
            "created_at": datetime.utcnow()
        },
        {
            "src_ip": "192.168.1.15",
            "dst_ip": "1.1.1.1",
            "src_port": 23456,
            "dst_port": 80,
            "protocol": "TCP",
            "severity": "medium",
            "description": "HTTP request detected",
            "created_at": datetime.utcnow()
        }
    ]
    return events
