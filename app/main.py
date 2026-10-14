from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(
    title="One Complaint, Five Departments",
    description="Prototype API for human-reviewed municipal grievance triage.",
    version="0.1.0",
)

# Small seed set for the feasibility demo. These are synthetic examples.
complaints = [
    {
        "id": "C-001",
        "text": "Water pipe is leaking near the bus stop",
        "channel": "web_portal",
        "location": "Ward 4",
        "department": "Water",
        "status": "received",
    },
    {
        "id": "C-002",
        "text": "Garbage has not been collected from the market road",
        "channel": "phone_transcript",
        "location": "Market Road",
        "department": "Sanitation",
        "status": "received",
    },
    {
        "id": "C-003",
        "text": "Street light is broken outside the community hall",
        "channel": "in_person",
        "location": "Ward 2",
        "department": "Electrical",
        "status": "received",
    },
    {
        "id": "C-004",
        "text": "Large open manhole near school, children could fall in",
        "channel": "social_media",
        "location": "Ward 5",
        "department": "Engineering",
        "status": "received",
    },
]

audit_log = []
SAFETY_TERMS = {
    "open manhole", "exposed wire", "fire", "gas leak", "collapse",
    "children could fall", "electric shock", "flooding road"
}
ROUTING_TERMS = {
    "Water": ["water", "pipe", "leak", "tap", "drainage"],
    "Sanitation": ["garbage", "waste", "rubbish", "cleaning", "smell"],
    "Electrical": ["street light", "electric", "wire", "lamp", "power"],
    "Engineering": ["road", "pothole", "manhole", "footpath", "bridge"],
}


class ComplaintIn(BaseModel):
    text: str = Field(min_length=5, max_length=5000)
    channel: Literal["web_portal", "phone_transcript", "social_media", "in_person"]
    location: Optional[str] = Field(default=None, max_length=250)


class ReviewIn(BaseModel):
    action: Literal["confirm_route", "edit_route", "reject_suggestion", "confirm_duplicate", "reject_duplicate"]
    staff_id: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=3, max_length=1000)
    selected_department: Optional[str] = None


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def suggest_department(text: str):
    lowered = text.lower()
    scores = {
        department: sum(1 for term in terms if term in lowered)
        for department, terms in ROUTING_TERMS.items()
    }
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return {"department": "Manual review", "confidence": 0.0,
                "reason": "No clear category keyword matched; staff review is needed."}
    total = sum(scores.values())
    confidence = round(scores[best] / max(total, 1), 2)
    return {
        "department": best,
        "confidence": confidence,
        "reason": f"Matched {scores[best]} keyword(s) associated with {best.lower()}.",
    }


def find_duplicates(text: str, exclude_id: Optional[str] = None):
    pool = [c for c in complaints if c["id"] != exclude_id]
    if not pool:
        return []
    corpus = [c["text"] for c in pool] + [text]
    matrix = TfidfVectorizer(ngram_range=(1, 2), lowercase=True).fit_transform(corpus)
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    matches = []
    for complaint, score in sorted(zip(pool, scores), key=lambda pair: pair[1], reverse=True):
        if float(score) >= 0.18:
            matches.append({
                "complaint_id": complaint["id"],
                "text": complaint["text"],
                "similarity": round(float(score), 3),
                "reason": "Shared words or phrases; staff must verify whether this is the same incident.",
            })
    return matches[:3]


def safety_flag(text: str):
    lowered = text.lower()
    matched = sorted(term for term in SAFETY_TERMS if term in lowered)
    return {
        "flagged": bool(matched),
        "matched_terms": matched,
        "note": "Flag is only a prompt for human review; it is not a safety assessment."
                if matched else "No configured safety phrase matched; this does not prove the complaint is safe."
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": app.title, "version": app.version}


@app.get("/complaints")
def list_complaints():
    return {"count": len(complaints), "items": complaints}


@app.post("/complaints", status_code=201)
def create_complaint(payload: ComplaintIn):
    record = {
        "id": f"C-{uuid4().hex[:8].upper()}",
        "text": payload.text,
        "channel": payload.channel,
        "location": payload.location,
        "department": None,
        "status": "received",
        "created_at": now_iso(),
    }
    complaints.append(record)
    return record


@app.post("/triage")
def triage(payload: ComplaintIn):
    route = suggest_department(payload.text)
    duplicates = find_duplicates(payload.text)
    safety = safety_flag(payload.text)
    return {
        "input": payload.model_dump(),
        "duplicate_candidates": duplicates,
        "routing_suggestion": route,
        "safety_review": safety,
        "decision_rule": "Suggestions are advisory. A staff member must review and record any consequential action.",
    }


@app.post("/review/{complaint_id}")
def review(complaint_id: str, payload: ReviewIn):
    record = next((c for c in complaints if c["id"] == complaint_id), None)
    if record is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    event = {
        "audit_id": f"A-{uuid4().hex[:8].upper()}",
        "complaint_id": complaint_id,
        "action": payload.action,
        "staff_id": payload.staff_id,
        "reason": payload.reason,
        "selected_department": payload.selected_department,
        "timestamp": now_iso(),
    }
    if payload.action in {"confirm_route", "edit_route"}:
        if not payload.selected_department:
            raise HTTPException(status_code=422, detail="selected_department is required for route decisions")
        record["department"] = payload.selected_department
        record["status"] = "staff_reviewed"
    audit_log.append(event)
    return {"recorded": True, "audit_event": event, "complaint": record}


@app.get("/audit")
def get_audit():
    return {"count": len(audit_log), "items": audit_log}
