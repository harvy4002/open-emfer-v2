# Implementation Plan: Camper Profile Status Photos

**Branch**: `009-camper-profile-status` | **Date**: 2026-07-13 | **Spec**: [specs/009-camper-profile-status/spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-camper-profile-status/spec.md`

## Summary

The Camper Profile Status feature replaces static fallback profile pictures on the public telemetry dashboard with dynamic status photos mapping directly to the camper's telemetry state. The implementation relies entirely on client-side JS string interpolation (`/<user_id>_status/<user_id>_<status>.jpg`) wrapped in a Bulma-responsive bounding box with native `onerror` fallbacks to avoid un-rendered or 404 images.

## Technical Context

**Language/Version**: Vanilla HTML/CSS/JS (Frontend)

**Primary Dependencies**: None (Bulma CSS via existing CDN)

**Storage**: AWS S3 Static Bucket (Asset Hosting)

**Testing**: Python Integration Scripts (`backend/test_endpoints.py`), local Python socket server.

**Target Platform**: Mobile-first Webb Browsers (iOS Safari, Android Chrome)

**Project Type**: Static Serverless Frontend Enhancement

**Performance Goals**: <300ms layout render on telemetry update

**Constraints**: Must execute 100% client-side to satisfy zero-cost serverless hosting constraints.

**Scale/Scope**: Impacts `web/index.html` and `web/js/app.js`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Contract-First)**: No backend API contracts are altered. Modifies frontend parsing purely based on existing payload structures.
- [x] **Principle II (Serverless Simplicity)**: N/A (Backend unaffected).
- [x] **Principle III (IaC)**: N/A (No new AWS structural resources introduced).
- [x] **Principle V (Zero-Trust Security)**: No secrets logged or modified.
- [x] **Principle VII (Cost-Optimized Static Frontends)**: 100% compliant. Status photo resolution is offloaded entirely to client-side JS executing natively in the browser against S3 assets, preventing server-side dynamic checks.
- [x] **Principle VIII (Fast Feedback Cycles)**: Can be verified immediately using the local python socket server on port 3000.

## Project Structure

### Documentation (this feature)

```text
specs/009-camper-profile-status/
├── plan.md              # This file
├── research.md          # Client-side native HTML onerror fallback research
├── data-model.md        # URL Routing Path definitions
├── quickstart.md        # Validation scenarios against backend simulator
└── tasks.md             # Implementation steps (to be generated)
```

### Source Code

```text
web/
├── index.html        # Modified: Responsive image container classes
└── js/
    └── app.js        # Modified: Replaces STATUS_IMAGES hardcode with dynamic interpolation
```

**Structure Decision**: Edits are contained purely inside the existing `web/` frontend directory layout matching the serverless single-page app architecture.

## Complexity Tracking

> *No complexity violations identified. Design relies purely on native DOM element string assignment and `onerror` event trapping.*
