# Implementation Plan: Web Push Notification Scheduler

**Branch**: `017-browser-notifications-scheduler` | **Date**: Wednesday, July 15, 2026 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-browser-notifications-scheduler/spec.md`

## Summary
The previous localized browser notification scheduler (`setInterval`) relies on the browser remaining active or running in the foreground. Mobile operating systems (iOS and Android) aggressively suspend background JavaScript tabs, meaning interval-based reminders fail to fire if the participant closes the browser or locks their phone for extended periods. To ensure robust reminder delivery, we are upgrading the system to use W3C Web Push Notifications via Service Workers.

## Scope & Impact
This transition from a purely client-side scheduler to a server-assisted push architecture will impact:
- **Frontend**: Introduction of a Service Worker (`sw.js`) and a Web App Manifest (`manifest.json`) to handle background pushes and enable PWA push capabilities on iOS. Modifications to `admin.js` to use `PushManager`.
- **Backend**: Modifications to `sim_server.py` to securely store push subscriptions and intervals, and the introduction of a background thread to schedule and dispatch encrypted payload events.
- **Dependencies**: Addition of the `pywebpush` library to sign and encrypt payloads according to the W3C Web Push protocol.

---

## Technical Context

**Language/Version**: Python 3.12 (AWS Lambda / simulation server) & Client Browser ECMAScript 6 JavaScript

**Primary Dependencies**: `pywebpush` (Python Web Push payload signing & encryption library), standard browser W3C Service Worker & Push APIs, Bulma CSS v1.0.0

**Storage**: AWS DynamoDB composite aggregate partitions or local JSON file `web/web_local_db.json`. Stores the `subscription` JSON payload and interval counters.

**Testing**: Pytest automated backend unit tests and local mobile/desktop Service Worker integration checks.

**Target Platform**: AWS Lambda, S3 Static Bucket, CloudFront CDN; or standard localhost simulator loop.

**Project Type**: Serverless Web Application (Frontend static assets + Serverless API Backend)

**Performance Goals**: Push subscription registrations verified and saved under 100ms; push payloads signed, encrypted, and dispatched within 60 seconds of interval boundaries.

**Constraints**: Strict compliance with browser HTTPS/secure context constraints; robust event loop structures in Python to check notifications without server degradation.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Contract-First)**: **PASS**. Fully specified in `spec.md` and caching variables configured in `data-model.md`.
- **Principle II (Serverless Simplicity)**: **PASS**. Built natively inside `sim_server.py` Lambda script with a single lightweight python library dependency `pywebpush`.
- **Principle IV (Database Modeling)**: **PASS**. Reuses the single-table composite keys in `camper#aggregates#<user_id>` totals to store subscriptions, preventing redundant tables.
- **Principle V (Zero-Trust Security)**: **PASS**. The subscription endpoint checks the secure, participant-specific `Authorization` header.
- **Principle VII (Cost-Optimized Static Frontend)**: **PASS**. Static files (manifest, sw.js, admin.js) reside in the static directory, costing $0 to host on CDN.
- **Principle VIII (Fast Feedback Loop)**: **PASS**. Local simulation server runs a background thread to send real, decrypted push notifications to Chrome/Safari on localhost in sub-second test boundaries.

---

## Project Structure

### Documentation

```text
specs/017-browser-notifications-scheduler/
├── spec.md              # Functional specification and user scenarios
├── plan.md              # Implementation plan (this file)
├── research.md          # Architectural research and decision record
├── data-model.md        # Extended storage schemas (localStorage keys)
├── quickstart.md        # Step-by-step validation guide
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code

```text
web/
├── admin.html           # Add manifest link inside the head section
├── manifest.json        # Create Web App Manifest enabling mobile PWA capabilities
├── sw.js                # Create Service Worker handling push and notification clicks
└── js/
    └── admin.js         # Register SW, PushManager subscribe, and POST push subscriptions
```

**Structure Decision**: Web application option.

---

## Complexity Tracking

*No Constitution Check violations or complexity deviations are identified. The design is completely clean, serverless, and lightweight.*
