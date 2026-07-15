# Implementation Plan: Additional Drinks Tracking and Dynamic Public Dashboard Breakdown

**Branch**: `015-additional-drinks-tracking` | **Date**: Wednesday, July 15, 2026 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/015-additional-drinks-tracking/spec.md`

## Summary

This feature adds four additional beverage logging categories (`Martini`, `G+T`, `Negroni`, `Port`) to the mobile-friendly administrative logging portal (`web/admin.html`). It also designs a dynamic, conditional "Drinks Breakdown" section on the public telemetry dashboard (`web/index.html` and `web/js/app.js`) that renders each beverage category (both newly added and existing categories) only if more than 1 unit has been consumed (count >= 2).

The implementation will be completed strictly using serverless vanilla architectures: modifying the Python standalone simulator/handler (`backend/sim_server.py`) and standard frontend scripts (`web/js/admin.js`, `web/js/app.js`), fully conforming to the project's development workflow.

---

## Technical Context

**Language/Version**: Python 3.12 (AWS Lambda / stand-alone simulation server) & Vanilla ECMAScript 6 Browser JS

**Primary Dependencies**: `boto3` (AWS SDK for Python DynamoDB), Bulma CSS v1.0.0 (responsive CSS framework), `pytest` & `coverage` (automated test suite)

**Storage**: Amazon DynamoDB composite-key table (`event` and `type` PK/SK) in production; Local JSON database `web/web_local_db.json` in offline simulator mode

**Testing**: Pytest automated unit/integration tests with overall coverage auditing gates (100% core logic coverage target)

**Target Platform**: AWS Lambda & API Gateway v2 HTTP API (Backend); Amazon S3 bucket & CloudFront CDN (Static Frontend distribution)

**Project Type**: Serverless Web Application (Frontend static assets + Serverless API Backend)

**Performance Goals**: Front-end assets initial load times of under 2 seconds on slow camper mobile networks; API transactions processed and cached under 500ms

**Constraints**: Mobile-first touch-friendly actions (min-48px heights); client-side lightweight rendering to avoid SSR server dynamic container costs; zero floor protection on all beverage category counters

**Scale/Scope**: Multi-user context isolation support for Harvy, Charlotte, Ash, and Tina; dual-write summation for the Combined Leaderboard

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Contract-First)**: **PASS**. The feature is fully specified in `spec.md` and the schemas are explicitly designed in `data-model.md` before writing code.
- **Principle II (Serverless Simplicity)**: **PASS**. The backend modifications will be made in the lightweight `sim_server.py` Lambda script, with zero additional Python packages or heavyweight dynamic frameworks.
- **Principle III (Infrastructure-as-Code)**: **PASS**. No new AWS infrastructure or Terraform resources are required since we are reusing the existing composite-key DynamoDB aggregate records.
- **Principle IV (Database Modeling)**: **PASS**. Reuses the high-efficiency `categories` map inside `camper#aggregates#<user_id>` without adding redundant database tables.
- **Principle V (Zero-Trust Security)**: **PASS**. All mutative API endpoints (POST to `/beer` and `/steps`) continue to enforce case-insensitive `Authorization` headers mapped to secure participant-specific keys.
- **Principle VI (Automated Testing)**: **PASS**. Existing unit and integration pytest suites will be expanded to assert Martini, G+T, Negroni, and Port logging behaviors, ensuring 100% core math and status logic coverage.
- **Principle VII (Cost-Optimized Static Frontend)**: **PASS**. Done as vanilla browser fetch bindings in HTML/CSS/JS with zero dynamic server container hosting overhead.
- **Principle VIII (Fast Feedback Cycles)**: **PASS**. Fully runnable and mockable locally on port 3000 using the python simulation server for instantaneous sub-second verification.

---

## Project Structure

### Documentation (this feature)

```text
specs/015-additional-drinks-tracking/
├── spec.md              # Functional specification and acceptance criteria
├── plan.md              # Implementation plan (this file)
├── research.md          # Architectural research and decision record
├── data-model.md        # Extended record schema blueprints
├── quickstart.md        # Verification scripts and runnable test curl recipes
└── checklists/
    └── requirements.md  # Quality gate requirements validation checklist
```

### Source Code (repository root)

```text
backend/
├── sim_server.py        # Standalone local simulator & AWS Lambda router (add drinks support)
└── tests/
    ├── unit/            # Expansion of math and resolver test suites
    └── integration/     # Expansion of playback and user flow telemetry tests

web/
├── index.html           # Public dashboard (add breakdown container)
├── admin.html           # Logging portal (add new drink logging buttons)
├── js/
│   ├── app.js           # Public dashboard controller (render conditional list)
│   └── admin.js         # Logging portal controller (support new counters)
└── web_local_db.json    # Local JSON database seed template
```

**Structure Decision**: Web application option. Backend routes reside in `backend/` and frontend responsive files reside in `web/`.

---

## Complexity Tracking

*No Constitution Check violations or complexity deviations are identified. The design is completely clean, serverless, and lightweight.*
