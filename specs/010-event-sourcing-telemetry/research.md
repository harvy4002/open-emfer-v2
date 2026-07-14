# Technical Research: Event Sourcing Implementation Strategy

## Unknowns & Clarifications (from Technical Context)

All previously identified unknowns from the specification phase have been thoroughly researched and resolved.

1. **How do we achieve an atomic dual-write inside DynamoDB without complicating local testing?**
   - *Investigation*: AWS DynamoDB supports `TransactWriteItems`, but our local testing fallback simply stores data in a flat JSON file via `db_put_item(event, type_val, attributes)`. Using transaction primitives directly would break local emulation (Principle VIII).
   - *Resolution*: Rather than utilizing complex DynamoDB transactions, the event log dual-write will be executed directly within the endpoint handlers (or a wrapped `db_put_event(user_id, event_type, payload)`) using two sequential `db_put_item` calls. Given the low-volume scale constraints (<1000 req/s), sequential puts ensure 100% compatibility with our local test server while fulfilling the immutable event store requirements.

2. **How to generate chronological, sortable UUIDs for event keys?**
   - *Investigation*: DynamoDB range queries require sort keys to be strictly lexicographically sortable to fetch "all events before X timestamp".
   - *Resolution*: Use the standard Python ISO 8601 UTC string (`datetime.now(timezone.utc).isoformat()`) concatenated with a short random uuid/hash or using `time.time_ns()` to guarantee uniqueness while remaining perfectly sortable in string queries.

3. **How does the `/playback` engine replay states?**
   - *Decision*: A dedicated `process_playback(user_id, until_timestamp)` function will initialize an empty `CamperAggregates` object in memory. It will query the event store for all `event_type` records (e.g. `Drinks`, `Toilet`, `steps`) up to `until_timestamp`, applying the exact same numeric offset logic currently found in `process_api_post`, sequentially.

## Technology Choices & Best Practices

1. **Database Schema**
   - **Decision**: Single-table composite-key design.
   - **Rationale**: `PK="camper#events#<user_id>"` and `SK="event#<iso8601_timestamp>#<uuid>"` perfectly aligns with the project's existing DynamoDB structures.

2. **Data Structure (Read vs Write Models)**
   - **Decision**: CQRS-lite pattern.
   - **Rationale**: Real-time dashboards exclusively fetch the cached read-model `totals` item (avoiding expensive DB scans on load), while the write-model stores the raw event log payload alongside updating the read-model.
