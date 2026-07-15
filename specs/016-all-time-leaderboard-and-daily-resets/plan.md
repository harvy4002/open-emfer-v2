# Implementation Plan: All-Time Leaderboard Steps and Daily Resets

**Branch**: `016-all-time-leaderboard-steps` | **Date**: Wednesday, July 15, 2026 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/016-all-time-leaderboard-and-daily-resets/spec.md`

## Summary

This feature designs automated daily telemetry resets (total drinks, categories, active steps) and implements cumulative all-time accumulators to power persistent ranks on the combined public dashboard.

The resets occur gracefully via lazy valuation on backend `POST` queries inside `backend/sim_server.py`. The frontend static assets (`web/index.html` and `web/js/app.js`) are updated to render two responsive, beautifully styled leaderboards: All-Time Beverage Rankings and All-Time Step Rankings.

---

## Technical Context

**Language/Version**: Python 3.12 (Lambda & Simulation Server) & Vanilla ECMA6 JS

**Primary Dependencies**: `boto3` (AWS SDK), `pytest` (tests), Bulma CSS v1.0.0 (frontend)

**Storage**: AWS DynamoDB composite partition table or offline local JSON DB file `web/web_local_db.json`

**Testing**: Pytest automated unit and integration tests with coverage auditing gates

**Target Platform**: AWS API Gateway, Lambda, S3 Static Bucket, CloudFront CDN

**Project Type**: Serverless Web Application

**Constraints**: Lazy evaluator checks run in under 5ms, ensuring no cold start or runtime degradation; mobile-responsive columns

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Contract-First)**: **PASS**. Fully specified in `spec.md` and `data-model.md` before writing code.
- **Principle II (Serverless Simplicity)**: **PASS**. Built using pure standard-library date logic and boto3 dictionary extensions inside `sim_server.py`.
- **Principle IV (Safe DB Modeling)**: **PASS**. Extends the composites in `camper#aggregates#<user_id>` without adding slow secondary indices or tables.
- **Principle VII (Cost-Optimized Static Frontend)**: **PASS**. Done as browser-native HTML/JS rendering, maintaining zero dynamic SSR server running costs.
- **Principle VIII (Fast Feedback Loop)**: **PASS**. Fully runnable and mockable locally on port 3000 using the simulation server environment.

---

## Project Structure

### Documentation (this feature)

```text
specs/016-all-time-leaderboard-and-daily-resets/
├── spec.md              # Functional specification and user scenarios
├── plan.md              # Implementation plan (this file)
├── research.md          # Architectural decision record
├── data-model.md        # Extended record schema blueprints
├── quickstart.md        # Verification quickstart guide
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code (repository root)

```text
backend/
├── sim_server.py        # Add lazy date checks, daily reset event append, and all-time accumulators
└── tests/
    ├── unit/            # Add unit tests asserting UTC day-boundary resets
    └── integration/     # Add integration tests checking combined scoreboard sort order

web/
├── index.html           # Add All-Time Steps and All-Time Drinks columns
└── js/
    └── app.js           # Query, sort, and render all-time lists dynamically
```

**Structure Decision**: Web application option.

---

## Complexity Tracking

*No Constitution Check violations or complexity deviations are identified.*
