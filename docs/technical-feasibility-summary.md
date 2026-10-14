# Technical Feasibility Summary

## Objective
Demonstrate the core technical path for a grievance triage assistant without claiming production readiness.

## Proof points in this repository
1. **API shape:** FastAPI exposes health, intake, triage, review and audit endpoints.
2. **Duplicate candidate search:** TF-IDF vectors and cosine similarity return candidate records for human checking.
3. **Department suggestion:** a transparent keyword baseline returns a suggested department and reason.
4. **Safety prompt:** configured phrases trigger a human-review flag; absence of a flag is not proof of safety.
5. **Human control:** review actions require a staff ID and reason; route decisions require a selected department.
6. **Testability:** pytest smoke tests exercise the API and a validation rule.
7. **Data exploration:** a notebook inspects the synthetic CSV and plots category counts.
8. **Interface concept:** a static HTML wireframe illustrates how staff could review suggestions.

## Known gaps
This proof does not establish model accuracy, production scalability, privacy compliance, multilingual performance, or suitability for real public-service use. The sample is synthetic and small. Persistent storage, authentication, access control, deployment hardening and integration are future work.
