# Implementation Plan: Public Landing Page and Dynamic Dashboard Routing

**Branch**: `008-public-landing-page` | **Date**: 2026-07-12 | **Spec**: [specs/008-public-landing-page/spec.md](./spec.md)

**Input**: Feature specification from `specs/008-public-landing-page/spec.md`

## Summary

The **Public Landing Page and Dynamic Dashboard Routing** feature transforms the root of the main dashboard site. 

This implementation plan establishes the design for a single-page conditional toggle inside `web/index.html`. When loaded without any camper identifiers, the DOM renders a clean, welcoming, informational landing page panel (`#intro-landing-view`) explaining the EMF Camp project goals. If accessed with specific camper parameters (like `?u=cha`), it completely bypasses the static introduction text and renders that participant's telemetry dashboard widgets. For Harvy's dashboard (`?u=hvy`), it also renders his exclusive T1000 GPS location trail on a provided campground map overlay.

---

## Technical Context

**Language/Version**: Browser-native HTML5 / ES6 Vanilla JavaScript.

**Primary Dependencies**: Bulma CSS v1.0.0 (responsive layout styling), browser-native standard History APIs (`pushState` and `popstate` events).

**Storage**: None (purely client-side session routing state).

**Testing**: Local static web preview on `http://localhost:8080/index.html`.

**Target Platform**: S3 + CloudFront CDN Static Assets (UK London Region `eu-west-2`).

**Project Type**: Static web application.

**Performance Goals**: Page routing transitions in under 100ms, and total asset footprint minimal for fast cellular downloads.

**Constraints**: Mobile-responsive structural compliance down to 320px screen widths, tactile 48px touch targets for navigation.

**Scale/Scope**: Supports 4 direct camper dashboards (`hvy`, `cha`, `ash`, `tin`) and the `combined` totals stats view, with exclusive T1000/Browan environmental charts and campground route map overlays restricted strictly to `hvy`.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check Status | Details / Adherence Strategy |
|-----------|--------------|------------------------------|
| **I. Contract-First** | ✅ PASS | Aligned with client-side UI configurations. Bypassing uses local parameter rules, not altering remote database schemas. |
| **II. Serverless Simplicity** | ✅ PASS | Implemented purely client-side without any server-side processors, node compilation pipelines, or framework overhead. |
| **III. Infrastructure-as-Code** | ✅ PASS | Frontend assets are static files served from AWS S3 CDN modeled via Terraform. |
| **IV. Database Modeling** | ✅ PASS | Telemetry reads map to standard partition/sort key conventions without any database structural changes. |
| **V. Zero-Trust Security** | ✅ PASS | Adheres to strict authorization practices; the landing page is public and read-only, maintaining secure header keys only on mutative calls. |
| **VI. Automated Testing** | ✅ PASS | Simple browser-native manual test cases and offline-runnable static page serves. |
| **VII. Cost-Optimized Frontends**| ✅ PASS | Served purely from S3website + CloudFront. Conditional UI toggling eliminates dynamic server costs or SSR page routing. |
| **VIII. Fast Feedback Cycles** | ✅ PASS | Runnable and testable locally in sub-seconds via standard `python3 -m http.server -d web 8080` command. |

---

## Project Structure

### Documentation (this feature)

```text
specs/008-public-landing-page/
├── spec.md              # Feature specification
├── plan.md              # This file (Technical layout and planning gates)
├── research.md          # Technical analysis of unified rendering mechanics
├── data-model.md        # DOM visibility states and parameter mapping
├── quickstart.md        # Runnable verification scenarios
└── checklists/
    └── requirements.md  # Requirements completeness checklist
```

### Source Code (repository root)

```text
web/
├── index.html           # Main dashboard web entry (Updates)
└── js/
    └── app.js           # Client-side router & widgets loader (Updates)
```

**Structure Decision**: Single project layout. We will modify `web/index.html` to add the `#intro-landing-view` container with the project explanation and participant buttons, and wrap the telemetry panels in `#dashboard-view`. We will update `web/js/app.js` to implement the condition checker and `pushState` transitions.

---

## Complexity Tracking

> *No current violations identified. Single-page client-side toggling represents the simplest possible technical design with zero dynamic running costs.*
