# One Complaint, Five Departments
## Technical Feasibility Proof — AI Synergy Hackathon 2026, Case 07: Governance

This repository is a small proof of concept for a human-in-the-loop municipal grievance triage assistant. It demonstrates that the main workflow can be implemented: receive a complaint, find similar records, suggest a department, flag possible safety wording, and record a staff decision.

**Important:** This is a prototype using a small synthetic dataset. It is not connected to a real municipal system and must not be used for live complaints. The routing and duplicate-matching logic is a baseline, not a validated production model.

### What is included
- `app/main.py` — FastAPI prototype with intake, triage, review and audit endpoints.
- `data/synthetic_complaints.csv` — illustrative synthetic complaint records.
- `notebooks/dataset_exploration.ipynb` — simple exploration of the sample dataset.
- `tests/test_api.py` — API smoke tests.
- `docs/architecture.md` — architecture and data-flow diagram (Mermaid).
- `docs/pseudocode.md` — core workflow pseudocode.
- `wireframe/index.html` — static staff dashboard wireframe.
- `requirements.txt` — dependencies.

### Run locally
Use Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation and `http://127.0.0.1:8000/health` to check the service.

### Run the tests
```bash
pytest -q
```

### Try the triage endpoint
```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text":"Water is leaking from a pipe near the bus stop","channel":"web_portal","location":"Ward 4"}'
```

### API endpoints
- `GET /health` — service status.
- `GET /complaints` — list stored prototype complaints.
- `POST /complaints` — add a complaint.
- `POST /triage` — return duplicate candidates, department suggestion and safety flag.
- `POST /review/{complaint_id}` — record a staff decision.
- `GET /audit` — view recorded review actions.

### Current limitations
- The demo stores records in memory; restarting the server resets changes.
- Similarity uses TF-IDF and cosine similarity, suitable for a basic English-language feasibility demo only. Hindi and mixed-language support needs proper multilingual embeddings and language-wise evaluation.
- Safety detection is a simple keyword flag and is not a safety classifier.
- Authentication, role-based access, persistent storage, production privacy controls and live integrations are not implemented.
- No complaint is automatically merged, closed, rejected, reassigned or deprioritised.

### Evidence to capture for submission
1. Screenshot of `/docs` showing the endpoints.
2. Screenshot of a successful `/health` response.
3. Screenshot of a `/triage` response.
4. Screenshot of `pytest -q` passing.
5. Once uploaded, paste the public GitHub repository URL into the competition form.
