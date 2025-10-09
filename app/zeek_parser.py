from app.threat_manager import log_threat_to_db

def parse_zeek_event(event: dict):
    """
    Example Zeek event dict:
    {
        "host_id": "host1",
        "src_ip": "192.168.1.10",
        "event_type": "portscan",
        "event_text": "Portscan detected"
    }
    """
    return log_threat_to_db(
        host_id=event["host_id"],
        src_ip=event["src_ip"],
        event_type=event["event_type"],
        event_text=event["event_text"]
    )
