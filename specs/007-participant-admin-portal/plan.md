# Implementation Plan: Participant Admin Portal

**Branch**: `007-participant-admin-portal` | **Date**: 2026-07-12 | **Spec**: [specs/007-participant-admin-portal/spec.md](./spec.md)

**Input**: Feature specification from `specs/007-participant-admin-portal/spec.md`

## Summary

The **Participant Admin Portal** is an authenticated, mobile-first static web interface designed to let campsite participants log telemetry data, track learning sessions, and manage their status in real time. 

This implementation plan establishes the design for **bi-directional item counters** (plus/minus tactile targets) displaying live aggregate values directly inside the admin console, and integrating secure decrement ("reverse") transactions with the backend API to correct accidental logging events without needing to access the public dashboard.

---

## Technical Context

**Language/Version**: Browser-native HTML5 / ES6 Vanilla JavaScript, Python 3.12 (backend lambdas & simulator).

**Primary Dependencies**: Bulma CSS v1.0.0 (responsive dark styling via CDN), standard browser `fetch` API, no heavy modern compilers or JavaScript build pipelines.

**Storage**: Amazon DynamoDB (On-Demand capacity) on AWS, and standard browser `localStorage` for caching credentials.

**Testing**: Python `pytest` for Lambda handlers, local standard HTTP simulation via `backend/sim_server.py`.

**Target Platform**: AWS S3 Static Website Hosting + AWS CloudFront CDN distribution for near-zero dynamic hosting costs (Principle VII).

**Project Type**: Serverless static web application + Python REST micro-services.

**Performance Goals**: UI load time under 1 second on cellular connections, action/reversal execution in under 500ms.

**Constraints**: Mobile-first touch compliance (minimum 48px touch targets, relative scaling down to 320px viewport), and failure notifications for poor campground network coverage.

**Scale/Scope**: Designed for 3 primary campers (`hvy`, `ali`, `bob`) with independent bookmarks and secure link context locking.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check Status | Details / Adherence Strategy |
|-----------|--------------|------------------------------|
| **I. Contract-First** | ✅ PASS | Adheres strictly to the `/beer` endpoint structure documented in `openapi.json` and [Contracts](./contracts/beer-post.json). |
| **II. Serverless Simplicity** | ✅ PASS | Frontend consists of static, compiling-free web assets (`admin.html`, `js/admin.js`). Backend logic uses standard Python AWS Lambdas. |
| **III. Infrastructure-as-Code** | ✅ PASS | Frontend deployed using AWS S3 website buckets and CloudFront modeled in Terraform (`tf/`). |
| **IV. Database Modeling** | ✅ PASS | Data stores map directly to partition keys (`camper#aggregates#<user_id>`) and sort keys (`totals`) in single-table DynamoDB. |
| **V. Zero-Trust Security** | ✅ PASS | Authorization utilizes the `tracker_key` header, cached securely in browser `localStorage`. No hardcoded credentials. |
| **VI. Automated Testing** | ✅ PASS | Backend endpoints mockable and verifiable offline via Python unit tests and the mock simulator server. |
| **VII. Cost-Optimized Frontends**| ✅ PASS | Frontends compile to pure static assets served from CloudFront, keeping Dynamic Lambda and dynamic compute costs strictly to `POST` request execution. |
| **VIII. Fast Feedback Cycles** | ✅ PASS | Runnable and testable locally via `sim_server.py` serving static pages on `8080` and mock endpoints on `3000`. |

---

## Project Structure

### Documentation (this feature)

```text
specs/007-participant-admin-portal/
├── spec.md              # Feature specification
├── plan.md              # This file (Technical layout and planning gates)
├── research.md          # Technical analysis of bi-directional API features
├── data-model.md        # Remote DynamoDB partitions and localStorage keys
├── quickstart.md        # Runnable verification scenarios
└── contracts/           # API JSON contracts
    ├── beer-get.json    # GET /beer?user_id=... payload schema
    ├── beer-post.json   # POST /beer increment/decrement payload schema
    └── history-get.json # GET /history?user_id=... step-count schema
```

### Source Code (repository root)

```text
backend/
└── sim_server.py        # Local API & static server mockup

web/
├── admin.html           # Participant Admin entry markup
├── index.html           # Public dashboard entry markup
└── js/
    ├── admin.js         # Admin page logic controller (Updates)
    └── app.js           # Public page controller
```

**Structure Decision**: Web application layout. The static frontend assets live in `/web/` and call the serverless REST endpoints served by standard AWS API Gateway / Lambda functions. Local simulation is run entirely through `backend/sim_server.py`.

---

## Complexity Tracking

> *No current violations identified. Implementation aligns perfectly with serverless constraints and single-table DynamoDB patterns.*
