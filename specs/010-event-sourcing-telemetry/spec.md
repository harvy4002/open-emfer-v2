# Feature Specification: Event Sourcing for Telemetry and Aggregates

**Feature Branch**: `010-event-sourcing-telemetry`

**Created**: 2026-07-13

**Status**: Ready

**Input**: User description: "ensure the system is using event sourcing, as I want to recreate previous states. In the database specifically I'd like to see the events, the aggregate"

---

## Purpose and Overview

The **Event Sourcing for Telemetry and Aggregates** feature introduces a standard Event Sourcing pattern for the Open EMF Camper system. Currently, the backend operates on a state-overwrite or incremental counter update model, which only retains the current running state.

To support auditing, historical tracing, and accurate reconstruction of previous states at any point in time:
- The backend will write an immutable, discrete **event log record** into the database for every single mutative telemetry input (drinks logged, steps walked, noise detected, monzo transactions sync'd).
- The backend will also maintain the **running aggregate state** (totals/standings) in the database via atomic writes or dual-writes.
- The API will expose a dynamic **recreation/playback endpoint** that fetches the historical event stream and recomputes the state sequentially up to a target timestamp.

This ensures that developers and administrators can view the complete immutable audit trail of discrete events, alongside the cached, low-latency current aggregate state.

---

## Clarifications

### Session 2026-07-13
- **Q**: Should the system always replay from the absolute beginning of the event store, or use periodic snapshots? → **A**: Store all events in the event store, but store and update the latest state snapshot (running aggregates) in the database. The public dashboards will exclusively query and use the latest cached snapshots for rendering, while the complete event store is preserved for historical analysis and playback queries.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Immutable Event Recording (Priority: P1) 🎯 MVP

As a campsite developer, I want every telemetry ingestion request to write an immutable event log record to the database while updating the running aggregate, so that I can see both the raw historical event stream and the current state in the database table.

**Why this priority**: Foundational requirement for Event Sourcing. Every change must be securely captured as an immutable log event.

**Independent Test**: Submit 3 separate drink increment requests for user `hvy` (e.g. 1 Lager, 1 Coffee, 1 IPA). Query the database and verify that 3 separate immutable event items exist under `camper#events#hvy`, alongside 1 updated `totals` aggregate record containing `total_drinks` = 3.

**Acceptance Scenarios**:

1. **Given** a telemetry POST request is received for user `hvy`, **When** the transaction executes, **Then** the database inserts a new immutable event log item (with unique ID, event type, payload, and millisecond-precision timestamp) and updates the cached running aggregate item.
2. **Given** a new event is recorded, **When** reviewing the database, **Then** previously inserted event records remain untouched and unmodified.

---

### User Story 2 - State Reconstruction / Playback (Priority: P2)

As a camp analyst, I want to query a playback endpoint with a specific target timestamp, so that the system dynamically recreates the exact historical aggregate state as of that second by replaying events.

**Why this priority**: Crucial for diagnostic tracing, audit support, and correcting telemetry recording errors.

**Independent Test**: Log 3 drink events at 12:00:00, 12:05:00, and 12:10:00. Call the playback route with a target limit of `until=12:06:00`. Verify that the reconstructed state returns exactly `total_drinks` = 2, proving the previous state at that moment is recreated accurately.

**Acceptance Scenarios**:

1. **Given** multiple events are stored in the database over time, **When** the playback endpoint is requested with `until=<timestamp>`, **Then** the system retrieves only the events created on or before that timestamp and plays them back in-memory to return the historical aggregate state.
2. **Given** no events exist for a camper prior to the target timestamp, **When** playback is requested, **Then** the system returns a blank fallback state gracefully.

---

### Edge Cases

- **Out of Order Logs**: Telemetry packets received out of order due to poor connectivity. (The playback engine must sort retrieved events strictly by their recorded event timestamps before replaying them).
- **Duplicate/Idempotent Actions**: Packets retransmitted by LoRa gateway. (Each event must incorporate a unique packet/event transaction identifier to ensure idempotent playbacks).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Immutable Event Logging)**: All mutative POST endpoints (drinks, steps, noise, monzo sync) MUST insert an immutable discrete event record item into the database representing the action.
- **FR-002 (Composite Key Schema)**: Event records MUST be stored in the DynamoDB table using the partition key `camper#events#<user_id>` and the sort key `event#<timestamp_uuid>` to maintain clean single-table organization.
- **FR-003 (Event Payload Structure)**: Each event record MUST store: `event_id` (UUID), `user_id`, `event_type` (e.g. `beer_logged`, `steps_logged`), `payload` (arbitrary JSON containing specific delta numbers/attributes), and `timestamp` (ISO 8601 UTC format).
- **FR-004 (Running State Aggregates)**: The system MUST maintain the active aggregate totals inside `camper#aggregates#<user_id>` as the "read model" to support low-latency dashboard loads.
- **FR-005 (State Playback API)**: The API MUST expose a GET endpoint `/playback?user_id=<user_id>&until=<timestamp_iso>` that retrieves, sorts, and recomputes the aggregate state by sequentially applying all events.
- **FR-006 (Snapshot-First Dashboard Loads)**: For low-latency visual performance, the camper dashboards MUST exclusively query and render the latest cached state snapshot (running aggregates) stored in `camper#aggregates#<user_id>`. The complete event store MUST be preserved for analytical queries and historical playback.

### Key Entities *(include if feature involves data)*

- **TelemetryEvent**: Immutable log representing a single metric write. Attributes: `event_id`, `user_id`, `event_type`, `payload`, `timestamp`.
- **CamperAggregates**: Read-model/Snapshot representing current accumulated counters. Attributes: `user_id`, `total_drinks`, `beer_drinks`, `categories`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of telemetry writes generate both a secure event record and an aggregate update in a single transaction/dual-write under 200ms.
- **SC-002**: Playback state reconstruction of up to 100 consecutive events executes in-memory and returns the historical payload in under 500ms.
- **SC-003**: The playback engine tolerates missing metadata by gracefully applying default values without raising runtime exceptions or crashing.
- **SC-004**: No event record, once written, can be edited or deleted by standard consumer API operations (Read-Only Event Log).

---

## Assumptions

- **Assumption 1**: The event logging structure utilizes the same composite DynamoDB table (`open_emfer_v2_production`) to preserve single-table patterns (Principle IV).
- **Assumption 2**: Standard telemetry updates represent relatively small event streams (fewer than 5000 events per camper), meaning in-memory full replay is highly viable and cost-effective.
- **Assumption 3**: Standard millisecond-precision timestamps are sufficient to guarantee chronological event sequence ordering.
