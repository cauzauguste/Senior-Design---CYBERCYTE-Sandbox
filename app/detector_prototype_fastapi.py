from fastapi import FastAPI
from pydantic import BaseModel
from app.threat_manager import log_threat_to_db

app = FastAPI()

class GenerateEventRequest(BaseModel):
    host_id: str
    src_ip: str
    event_type: str
    event_text: str

@app.post("/generate_event")
def generate_event(event: GenerateEventRequest):
    logged_event = log_threat_to_db(
        host_id=event.host_id,
        src_ip=event.src_ip,
        event_type=event.event_type,
        event_text=event.event_text
    )
    return {"status": "ok", "event_id": logged_event.id}
