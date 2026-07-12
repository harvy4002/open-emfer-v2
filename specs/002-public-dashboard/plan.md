# Implementation Plan: Grafana-Style Public Dashboard and Participant Admin

**Branch**: `002-public-dashboard` | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-public-dashboard/spec.md`

**Note**: This plan establishes the frontend architecture, CDN deployment patterns, and UI state-preservation rules for the Grafana-style Public Dashboard and Participant Admin, in complete alignment with Principle VII (Cost-Optimized Serverless Frontends) of the Constitution.

## Summary

This feature delivers a highly responsive, mobile-first static web application hosted in Amazon S3 and distributed via AWS CloudFront CDN. It is split into two areas:
1. **Public Dashboard (`/` or `/index.html`)**: A dark-theme, grid-based dashboard inspired by Grafana's multi-panel visualizer. It pulls live metrics from the serverless API (drinks, camper statuses, temperature, decibels, Monzo spend) using native `fetch` requests, updating panels automatically every 60 seconds.
2. **Participant Admin (`/admin/` or `/admin.html`)**: An authenticated admin interface prompting campers for the `tracker_key` (saved locally in browser storage) and exposing forms to manually log activities, drinks, starts/stops of sessions, or trigger a tracker reset.

## Technical Context

**Language/Version**: Vanilla HTML5, Vanilla CSS, and modern Vanilla ES6+ JavaScript.

**Primary Dependencies**: 
* **Bulma CSS (via CDN)**: For responsive layout grids and structural UI elements.
* **Chart.js (via CDN)**: A lightweight browser-native charting library to render trend lines and gauges without introducing complex NPM build pipelines (Assumption 2).

**Storage**: Browser `localStorage` (Key Entities, Assumption 3) for:
* Caching user dashboard preferences (panel layout choices, line/bar toggles).
* Caching the `tracker_key` authorization token to preserve admin login sessions.

**Testing**: Browser-native testing scripts verifying responsive breakpoints and mock HTTP responses.

**Target Platform**: Amazon S3 Static Website buckets fronted by AWS CloudFront CDN with edge-caching policies (Principle VII).

**Project Type**: web-application (pure static).

**Performance Goals**: Dashboard fully interactive in < 2 seconds (SC-001) over slow camper networks.

**Constraints**:
* No Node.js build pipelines (Webpack, Vite, or React) to keep browser assets lightweight, fast-loading, and cost-free to host (Technical Constraints).
* All mutative forms in the admin area strictly require an authorization header containing the correct `tracker_key` (SC-004).

**Scale/Scope**: Serves high-traffic public camper audiences without incremental server running costs.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Standard | Status | Verification & Alignment |
| :--- | :--- | :--- |
| **I. Contract-First Development** | ✅ PASS | Relies strictly on the schemas and endpoints defined in the core API contract (`openapi.json`). |
| **II. Serverless Simplicity** | ✅ PASS | Frontend assets are static (HTML/CSS/JS), meaning zero backend servers or active runtimes to manage. |
| **III. Infrastructure-as-Code** | ✅ PASS | S3 bucket permissions, CloudFront distributions, and route behaviors modeled strictly in Terraform (`tf/`). |
| **IV. Safe Database Keys** | ✅ PASS | Frontend queries data using standard GET endpoints, respecting the single-table layout limits (e.g. max 20 location entries). |
| **V. Zero-Trust Security** | ✅ PASS | `tracker_key` stored locally in the admin's browser is loaded dynamically into authorization headers on mutative logs. |
| **VI. Automated Testing** | ✅ PASS | Endpoints queried by the browser are fully mocked in local testing files. |
| **VII. Cost-Optimized S3 Frontends**| ✅ PASS | Developed purely as static files distributed via CloudFront CDN to keep hosting costs near-zero and speed sub-2s (SC-001). |

## Project Structure

### Documentation (this feature)

```text
specs/002-public-dashboard/
├── spec.md              # Feature specification
├── plan.md              # Technical implementation plan
├── research.md          # Technical research and choices
├── data-model.md        # Frontend state management layout
├── quickstart.md        # Scenario testing and validation guide
└── checklists/          # Feature checklists
    ├── requirements.md  # General spec quality checklist
    └── dashboard.md     # Specific dashboard quality checklist
```

### Source Code (repository root)

```text
web/
├── css/
│   └── style.css        # Grafana dark-theme visual parameters
├── js/
│   ├── app.js           # Live dashboard polling, Chart.js integrations, layouts
│   └── admin.js         # Forms submissions, validation, key persistence
├── index.html           # Public dashboard root entry (S3/CloudFront)
└── admin.html           # Participant Admin entry (S3/CloudFront)

tf/
├── s3_frontend.tf       # S3 buckets and permissions
├── cloudfront.tf        # CloudFront CDN distribution and caches
└── main.tf
```

**Structure Decision**: Codebase structured as a flat `web/` static assets folder for clean S3 syncing, and Terraform `tf/` folder for CDN orchestration.

## Complexity Tracking

*No Constitution violations detected. The static design is 100% compliant with Open EMF Camper serverless frontend constraints.*
