# Implementation Plan: Event Sourcing for Telemetry and Aggregates

**Branch**: `010-event-sourcing-telemetry` | **Date**: 2026-07-13 | **Spec**: [specs/010-event-sourcing-telemetry/spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-event-sourcing-telemetry/spec.md`

## Summary

This feature implements a robust CQRS Event Sourcing architecture. It enhances the existing mutative telemetry endpoints (`/beer`, `/steps`, `/sensecap`, `/browan`, `/monzo-sync-simulation`) to securely dual-write an immutable `TelemetryEvent` log alongside the current aggregate snapshot. Additionally, it exposes a new `/playback` API endpoint capable of querying the historical event store and executing an in-memory chronological state reconstruction up to any given target timestamp.

## Technical Context

**Language/Version**: Python 3.12 (AWS Lambda)

**Primary Dependencies**: `json`, `datetime`, `uuid` (Python Standard Library), `boto3`

**Storage**: Amazon DynamoDB (Single-Table Design)

**Testing**: `backend/test_endpoints.py`, Local Socket Simulator

**Target Platform**: AWS API Gateway + Lambda

**Project Type**: Serverless REST API Backend

**Performance Goals**: <500ms playback reconstruction time

**Constraints**: Must maintain exactly the existing DynamoDB composite key structure without introducing complex `TransactWriteItems` that would break local file-based emulation.

**Scale/Scope**: Impacts `backend/sim_server.py`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle II (Serverless Simplicity)**: The dual-write operation relies on sequential native logic calls, maintaining single-responsibility lightweight methods with zero framework bloat.
- [x] **Principle IV (DynamoDB Keys)**: `TelemetryEvent` uses the exact existing composite key format (`PK=camper#events#<user_id>`, `SK=event#<iso_timestamp>#<uuid>`).
- [x] **Principle VIII (Fast Feedback Cycles)**: Local file-based emulator seamlessly handles standard `db_put_item` operations for events without requiring local dynamodb clones.

## Project Structure

### Documentation (this feature)

```text
specs/010-event-sourcing-telemetry/
├── plan.md              # This file
├── research.md          # DynamoDB sequential vs transaction logic & CQRS boundaries
├── data-model.md        # Event schema mappings and composite key layouts
├── quickstart.md        # Test scenarios for log appending and /playback isolation
└── tasks.md             # Implementation phases (to be generated)
```

### Source Code

```text
backend/
├── sim_server.py        # Modified: Dual-write handlers and new /playback endpoint
└── test_endpoints.py    # Modified: Integration tests for the new /playback route
```

**Structure Decision**: No new infrastructure resources or files are necessary. The entire backend logic will be consolidated strictly inside the monolithic `sim_server.py` router to preserve lambda cold-start speed and simplicity.

## Complexity Tracking

> *No complexity violations. Single-table composite keys and sequential dual-writes satisfy the constraints perfectly.*
