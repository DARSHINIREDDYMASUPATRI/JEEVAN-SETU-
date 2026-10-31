from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="JeevanSetu API",
    version="0.1.0",
    description="Development scaffold. Demo data only; not for real patient or drone operations."
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

requests = {}
drones = {
    "JVS-DEMO-001": {
        "drone_id": "JVS-DEMO-001",
        "hospital_id": "HOSPITAL-DEMO-001",
        "authorisation_status": "demo_unverified",
        "availability": "available",
        "real_flight_enabled": False,
    }
}

class EmergencyRequest(BaseModel):
    patient_reference: str = Field(min_length=1, max_length=80)
    request_type: str = Field(pattern="^(physical_emergency|medicine|first_aid)$")
    description: str = Field(default="", max_length=1000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    consent_to_share: bool = False

class HospitalDecision(BaseModel):
    decision: str = Field(pattern="^(accepted|declined|closed)$")
    staff_reference: str = Field(min_length=1, max_length=80)

@app.get("/health")
def health():
    return {"status": "ok", "service": "jeevansetu-api", "mode": "development-demo"}

@app.get("/api/v1/hospitals")
def list_hospitals():
    # Replace sample records with a verified hospital directory before deployment.
    return [
        {"id": "HOSPITAL-DEMO-001", "name": "Demo Rural Community Hospital",
         "verified": False, "phone": None, "note": "Sample only; no real contact details."}
    ]

@app.post("/api/v1/requests", status_code=201)
def create_request(payload: EmergencyRequest):
    if payload.latitude is not None and not payload.consent_to_share:
        raise HTTPException(status_code=400, detail="Location sharing consent is required.")
    item_id = str(uuid4())
    item = {
        "id": item_id,
        **payload.model_dump(),
        "status": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notice": "Demo request only. No hospital has been notified."
    }
    requests[item_id] = item
    return item

@app.get("/api/v1/requests")
def list_requests():
    return list(requests.values())

@app.post("/api/v1/requests/{request_id}/decision")
def decide_request(request_id: str, payload: HospitalDecision):
    item = requests.get(request_id)
    if not item:
        raise HTTPException(status_code=404, detail="Request not found")
    item["status"] = payload.decision
    item["reviewed_by"] = payload.staff_reference
    return item

@app.get("/api/v1/drones")
def list_drones():
    return list(drones.values())

@app.post("/api/v1/drones/{drone_id}/dispatch-simulation")
def simulate_dispatch(drone_id: str):
    drone = drones.get(drone_id)
    if not drone:
        raise HTTPException(status_code=404, detail="Unknown drone")
    # Intentionally never commands a physical aircraft.
    return {
        "drone_id": drone_id,
        "status": "simulated_dispatch_only",
        "real_flight_enabled": False,
        "message": "No aircraft command was sent. Real operations require approved integrations and regulatory checks."
    }
