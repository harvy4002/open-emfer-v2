# Data Model: Event Sourcing for Telemetry and Aggregates

## 1. Domain Entities & Database Mapping

The Event Sourcing implementation adds a pure immutable append-only event log entity to the existing DynamoDB composite key structure.

### 1.1 TelemetryEvent (Write Model)

An immutable log representing a single metric write or status change.

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `event` (PK) | `string` | The partition key. Format: `camper#events#<user_id>` (e.g. `camper#events#hvy`). |
| `type` (SK) | `string` | The sort key. Format: `event#<iso8601_utc_timestamp>#<short_uuid>` (e.g. `event#2026-07-13T12:00:00.000Z#a1b2`). Ensures strict chronological ordering. |
| `user_id` | `string` | Target camper identifier. |
| `event_type`| `string` | Classification string mapping to the action (e.g. `Drinks`, `Toilet`, `steps`, `monzo`). |
| `payload` | `map` | The raw JSON structure submitted by the client (e.g. `{"beer": true, "type": "Lager"}`). |

### 1.2 CamperAggregates (Read Model / Snapshot)

The existing aggregated running totals. No schema changes are required here, but the architectural pattern shifts to treat this partition strictly as a cached snapshot.

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `event` (PK) | `string` | `camper#aggregates#<user_id>` |
| `type` (SK) | `string` | `totals` |
| `total_drinks`| `number` | Running accumulated counter. |

## 2. API Contract Extension

### `GET /playback`

Fetches and sequentially executes the in-memory reconstruction of a camper's state based exclusively on the immutable `TelemetryEvent` log up to the specified boundary.

**Request Query Parameters**:
* `user_id` (string): The camper shortcode (e.g. `hvy`).
* `until` (string, ISO 8601): The upper bounding timestamp (inclusive).

**Response Schema** (Matches the structure of standard aggregate totals):
```json
{
  "status": "success",
  "reconstructed_state": {
    "user_id": "hvy",
    "total_drinks": 2,
    "beer_drinks": 1,
    "categories": {
      "Lager": 1,
      "Water": 1
    }
  },
  "events_processed": 4,
  "playback_boundary": "2026-07-13T14:30:00Z"
}
```
