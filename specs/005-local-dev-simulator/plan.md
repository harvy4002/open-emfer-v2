# Implementation Plan: Local Developer Simulator

**Branch**: `005-local-dev-simulator` | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-local-dev-simulator/spec.md`

**Note**: This plan establishes the local Python static server configuration, CORS wildcards, JSON database schemas, and HTML5 simulator pages to fulfill Principle VIII (Fast Feedback Cycles) of the Constitution.

## Summary

This feature delivers a local-only interactive development sandbox consisting of:
1. **Local Static Assets Server**: Runs on `localhost:8080` (utilizing Python's standard `http.server` library) to serve your public and admin dashboards locally.
2. **Interactive API Playground (`web/simulator.html`)**: A web page that provides forms and randomized data presets to manually trigger mock API events, logging exact request/response JSON payloads.
3. **Local API Simulator (`backend/sim_server.py`)**: A lightweight, zero-dependency Python HTTP server running on port 3000. It simulates all production API Gateway routes, intercepts preflight requests with CORS headers, and persists state inside a local JSON file database (`web/web_local_db.json`).

## Technical Context

**Language/Version**: Python 3.12+, Vanilla HTML5, Vanilla ES6+ JavaScript.

**Primary Dependencies**: None (relying entirely on Python standard library modules `http.server` and `json` to ensure immediate, zero-installation setup).

**Storage**: Local JSON database file (`web/web_local_db.json`) caching simulated user aggregates, statuses, coordinates, and bank transactions.

**Testing**: Manual, browser-native scenario triggering.

**Target Platform**: Local developer workstation (cross-platform).

**Project Type**: web-service + web-application (local tooling).

**Performance Goals**: Processing and saving mock telemetry events in < 100ms.

**Constraints**:
* No node package installations or dependencies required on the host computer.
* Emulated endpoints must accept CORS preflight options requests and inject wildcard `Access-Control-Allow-Origin: *` headers (FR-005).

**Scale/Scope**: Single-workstation developer debugging sandbox.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Standard | Status | Verification & Alignment |
| :--- | :--- | :--- |
| **I. Contract-First Development** | ✅ PASS | Emulated endpoints strictly mirror request formats defined in `openapi.json` and Contracts. |
| **II. Serverless Simplicity** | ✅ PASS | Emulation server built on standard libraries, mirroring Lambda single-purpose route separation. |
| **III. Infrastructure-as-Code** | ✅ PASS | No live AWS infrastructure is provisioned for this feature. |
| **IV. Safe Database Keys** | ✅ PASS | The local JSON file database utilizes identical Partition Key (`event`) and Sort Key (`type`) structures. |
| **V. Zero-Trust Security** | ✅ PASS | Emulates token verification checks for `tracker_key` to replicate live authorization gates. |
| **VI. Automated Testing** | ✅ PASS | Local playground serves as the high-fidelity mock harness for frontend scripts. |
| **VII. Cost-Optimized Frontends**| ✅ PASS | Serves static HTML/CSS/JS identical to S3, verifying dynamic browser-native `fetch()` logic. |
| **VIII. Fast Feedback Cycles** | ✅ PASS | Direct implementation of the fast feedback loops, running everything 100% locally and offline. |

## Project Structure

### Documentation (this feature)

```text
specs/005-local-dev-simulator/
├── spec.md              # Feature specification
├── plan.md              # Technical implementation plan
├── research.md          # Technical research and choices
├── data-model.md        # Local JSON database schemas
├── quickstart.md        # Scenario testing and validation guide
└── checklists/
    └── requirements.md  # General spec quality checklist
```

### Source Code (repository root)

```text
backend/
└── sim_server.py        # Local Python API server (emulates Lambdas, port 3000)

web/
├── simulator.html       # Web-based interactive trigger playground
├── web_local_db.json    # Local JSON database file (Option B)
└── js/
    └── simulator.js     # Playground client logic (payload triggers & logging)
```

**Structure Decision**: Source code mapped directly inside the existing `backend/` and `web/` folders to keep structure unified, simple, and clean.

## Complexity Tracking

*No Constitution violations detected. The lightweight standard library design strictly conforms to serverless developer speed standards.*
