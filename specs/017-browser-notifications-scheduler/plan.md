# Implementation Plan: Browser Notifications Scheduler

**Branch**: `017-browser-notifications-scheduler` | **Date**: Wednesday, July 15, 2026 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-browser-notifications-scheduler/spec.md`

## Summary

This feature designs and implements standard browser-native reminder notifications inside the participant's manual admin logging portal (`web/admin.html` and `web/js/admin.js`). 

The system utilizes the browser W3C Notifications API to request permissions, schedules recurring reminder prompts using standard lightweight `setInterval` timers, and provides an active window refocus action on user click. Preferences are fully preserved on reloads using local `localStorage` keys, ensuring a seamless, zero-cost serverless experience.

---

## Technical Context

**Language/Version**: Vanilla Client Browser ECMAScript 6 JavaScript & HTML5 / CSS3 (Bulma CSS v1.0.0)

**Primary Dependencies**: None (Standard browser-native Notification API and Bulma styles), keeping the front-end extremely lightweight and dependency-free

**Storage**: Browser `localStorage` (client-side persistence), requiring **zero** server-side database table changes

**Testing**: Web browser standalone console checks and native notification testing routines

**Target Platform**: Any modern HTML5/W3C compliant browser served over a secure context (HTTPS / localhost)

**Project Type**: Standalone Static Frontend Integration

**Performance Goals**: Permissions requested and scheduled instantly under 50ms; sub-100ms click refocus reaction times

**Constraints**: Absolute 0 server/database running costs, fully matching Principle VII; robust background loop management to tear down timers cleanly when toggled off

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Contract-First)**: **PASS**. Fully specified in `spec.md` and caching variables configured in `data-model.md`.
- **Principle II (Serverless Simplicity)**: **PASS**. No serverless Python dependencies, Lambda cold starts, or additional AWS services are introduced.
- **Principle IV (Database Modeling)**: **PASS**. Operates 100% client-side, requiring zero database modifications.
- **Principle VII (Cost-Optimized Static Frontend)**: **PASS**. Designed strictly as standard browser Fetch/API interactions with $0 runtime hosting costs.
- **Principle VIII (Fast Feedback Loop)**: **PASS**. Instantly runnable and testable locally on port 3000 using the python simulation server.

---

## Project Structure

### Documentation (this feature)

```text
specs/017-browser-notifications-scheduler/
├── spec.md              # Functional specification and user scenarios
├── plan.md              # Implementation plan (this file)
├── research.md          # Architectural research and decision record
├── data-model.md        # Extended client-side storage blueprints
├── quickstart.md        # Step-by-step validation guide
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code (repository root)

```text
web/
├── admin.html           # Add Bulma card and toggle switch for notification reminder preferences
└── js/
    └── admin.js         # Register switch listeners, Notification API bindings, and background timers
```

**Structure Decision**: Web application option.

---

## Complexity Tracking

*No Constitution Check violations or complexity deviations are identified. The design is completely clean, serverless, and lightweight.*
