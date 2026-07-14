# Implementation Plan: Sensecap Location Map Integration

**Branch**: `013-sensecap-location-map` | **Date**: 2026-07-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/013-sensecap-location-map/spec.md`

## Summary
Integrate an interactive, responsive geographical map on the public telemetry dashboard that loads custom event cartography from the EMF Camp tile server (`map.emfcamp.org`), displays the active camper's current position, and plots their movement trail over the last 3 hours (relative to their latest coordinate check). This feature replaces the static background image placeholder with an interactive Leaflet.js widget, and adds a mock GPS route generator in the local dev simulator to facilitate automated testing and offline verification.

---

## Technical Context

**Language/Version**: 
- **Frontend**: Vanilla HTML5 / ES6 JavaScript / CSS3
- **Backend/Simulator**: Python 3.12+

**Primary Dependencies**:
- **Frontend**: Leaflet.js (v1.9.4) loaded via unpkg CDN, Bulma CSS (v1.0.0)
- **Backend**: Standard Python libraries (e.g., `json`, `datetime`)

**Storage**:
- **DynamoDB**: Composite-key single-table model (Partition Key `PK` = `device#eui-...`, Sort Key `SK` = `state`).
- **State Limits**: Capped location history array to a maximum of 20 elements (Compliance with Principle IV).

**Testing**:
- **Unit Testing**: `pytest` for backend simulation assertions.
- **Visual E2E Validation**: Run local simulation script and verify Leaflet path filters inside `web/index.html` and simulator payload injection in `web/simulator.html`.

**Target Platform**: 
- Responsive static web dashboard distributed via AWS CloudFront CDN and Amazon S3.

**Project Type**: Web Application (Serverless frontend calling AWS Lambda endpoints).

**Performance Goals**:
- Map loading and marker rendering in <1.5 seconds under standard mobile camper networks.

**Constraints**:
- Must fallback gracefully to OpenStreetMap tiles if `map.emfcamp.org` is unreachable.
- Must filter path coordinates client-side to keep server logic stateless and lightweight.

**Scale/Scope**:
- Displaying the active selected participant's path, but designed extensibly to support overlays for multiple concurrent campers in future iterations.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Rule | Compliance Status | Implementation Details |
| :--- | :--- | :--- |
| **I. Contract-First** | Compliant ✅ | Endpoint schemas `/sensecap` (POST) and `/history` (GET) are preserved and documented in `contracts/api-contracts.md`. |
| **II. Serverless Simplicity** | Compliant ✅ | Backend logic is implemented inside lightweight Python handlers with no heavy dependencies. |
| **III. Infrastructure-as-Code** | Compliant ✅ | Maps directly to current Lambda / API Gateway resources. No physical infra needs manual changes since static files are pushed to S3. |
| **IV. Safe DB Modeling** | Compliant ✅ | Maintains DynamoDB `PK`/`SK` composite keys and respects the 20-entry coordinate sequence bounds in the state schema. |
| **V. Zero-Trust Security** | Compliant ✅ | Ingestion endpoint `POST /sensecap` enforces authentication via the secure header `tracker_key`. |
| **VI. Automated Testing** | Compliant ✅ | Backed by unit tests verifying coordinate parsing, distance calculations, and chronological sorting. |
| **VII. Cost-Optimized Frontend** | Compliant ✅ | Developed using lightweight Vanilla HTML/CSS/JS (Leaflet CDN) hosted on S3 and distributed via CloudFront; 0% server running cost. |
| **VIII. Fast Feedback Cycles** | Compliant ✅ | Includes a local simulator preset to inject a mock 3-hour campsite trail instantly to test map rendering locally without AWS deployment. |

---

## Project Structure

### Documentation (this feature)

```text
specs/013-sensecap-location-map/
├── plan.md              # This file
├── research.md          # Map library, tiles, and filtering research
├── data-model.md        # Entities schema (LocationPoint, LocationHistoryState)
├── quickstart.md        # End-to-end runnable testing validation guide
├── contracts/
│   └── api-contracts.md # Ingestion and history retrieval payloads
└── checklists/
    └── requirements.md  # Quality verification checklist
```

### Source Code (repository root)

```text
backend/
├── sim_server.py        # Local simulation server (contains endpoints /sensecap, /history)
└── test_endpoints.py    # Local simulation endpoint unit tests

web/
├── index.html           # Public dashboard (loads Leaflet map widget)
├── simulator.html       # Simulator control panel (injects mock location history)
└── js/
    ├── app.js           # Client application logic (renders Leaflet map and filters last 3 hours)
    └── simulator.js     # Client simulator script (creates mock coord telemetry)
```

**Structure Decision**: Employs the standard multi-tier single repo setup (Option 2 - Web Application split into `backend/` simulation APIs and `web/` static frontend assets), ensuring perfect local execution alignment.

---

## Complexity Tracking

*No constitutional violations detected. Simplicity guidelines strictly adhered to.*
