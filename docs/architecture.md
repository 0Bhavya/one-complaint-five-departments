# Architecture and data flow

```mermaid
flowchart TD
    A[Web portal / phone transcript / social media / office entry] --> B[Intake API - FastAPI]
    B --> C[Preserve original text + basic validation]
    C --> D[Text normalisation]
    D --> E[Duplicate candidate search - TF-IDF baseline]
    D --> F[Department suggestion - keyword baseline]
    D --> G[Safety phrase flag]
    E --> H[Staff review dashboard]
    F --> H
    G --> H
    H --> I{Staff decision}
    I -->|Confirm / edit / reject| J[Audit log]
    J --> K[Complaint record updated only after staff action]
    K --> L[Draft factual status update]
    H -->|Low confidence / conflict| M[Manual review queue]
```

## Trust boundary
The model returns suggestions only. A staff member must confirm a routing or duplicate action. The prototype uses in-memory storage and synthetic data; PostgreSQL, authentication, and live integrations are future work.
