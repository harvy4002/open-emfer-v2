# Implementation Plan: Event-Sourced Camper Status Image Matching

**Branch**: `012-camper-status-event-sourcing` | **Date**: 2026-07-13 | **Spec**: [specs/012-camper-status-event-sourcing/spec.md](./spec.md)

**Input**: Feature specification from `/specs/012-camper-status-event-sourcing/spec.md`

## Summary

This feature establishes an event-sourced storage schema for camper status actions. It ensures that the active visual portrait shown on individual dashboards is strictly driven by explicit status clicks, ignoring any intermediate implicit telemetries. 

It accomplishes this through:
1. **Event Filtering**: The GET status API retrieves the event history and filters strictly for `"status"` or `"Status"` event categories.
2. **Keyword Fuzzy Resolution**: The frontend maps custom status strings (e.g. *Coding*, *Nap*, *Pee*) to the exact 11 local photographic JPG assets.

## Technical Context

**Language/Version**: Python 3.12 (AWS Lambda / Backend), Vanilla HTML/CSS/JS (Frontend)

**Primary Dependencies**: Bulma CSS (CDN), Boto3 (AWS SDK)

**Storage**: AWS DynamoDB (Composite Keys PK `"camper#events#<user_id>"` and SK `"event#<iso_timestamp>#<short_uuid_hash>"`)

**Testing**: Walkthrough scenarios on local port 3000 and live AWS Lambda checks

**Target Platform**: Mobile and Desktop viewports

**Project Type**: Serverless Full-Stack Event Sourcing Sync

**Performance Goals**: <300ms visual refresh latency

**Constraints**: Bypasses any implicit sensor event types when resolving the active camper profile photo.

**Scale/Scope**: Impacts `backend/sim_server.py`, `web/index.html`, and `web/js/app.js`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle II (Serverless Simplicity)**: 100% compliant. Bypasses account-specific KMS variables and maintains standard boto3 operations.
- [x] **Principle IV (Safe Database Keys)**: 100% compliant. Implements partition key `camper#events#<user_id>` and lexicographically sortable sort key `event#<iso_timestamp>#<short_uuid_hash>`.
- [x] **Principle VII (Cost-Optimized Static Frontends)**: 100% compliant. Offloads the heavy keyword fuzzy resolver entirely inside browser JS, saving server compute overhead.

## Project Structure

### Documentation (this feature)

```text
specs/012-camper-status-event-sourcing/
├── plan.md              # This file
├── research.md          # Database query filtering vs absolute queries
├── data-model.md        # Keyword lookup mapping pairs
├── quickstart.md        # Walkthrough validation checks
└── tasks.md             # Implementation steps (to be generated)
```

### Source Code

```text
backend/
└── sim_server.py     # Modified: Filters query logs for explicit status events

web/
├── index.html        # Modified: Pins double-fallback onerror parameters
└── js/
    └── app.js        # Modified: Integrates resolveStatusImage and window.activeUser
```

## Complexity Tracking

> *No complexity violations identified. Event filtering uses simple array comprehensions, and keyword mapping uses regex/includes checks.*
