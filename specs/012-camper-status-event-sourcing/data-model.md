# Data Model: Event-Sourced Camper Status Image Matching

The storage and client-side mappings operate strictly on event-sourced partitions.

## 1. Domain Entities & URL Routing Structure

### 1.1 Status Event Structure (TelemetryEvent)

Each status change clicked in the manual panel logs a standard event:

| Table Attribute | DynamoDB Data Type | Value / Purpose |
| :--- | :--- | :--- |
| **event** | String (`S`) | Partition Key: `camper#events#<user_id>` |
| **type** | String (`S`) | Sort Key: `event#<timestamp>#<short_uuid_hash>` |
| **event_type** | String (`S`) | `"Status"` or `"status"` (case-insensitive) |
| **timestamp** | String (`S`) | ISO 8601 UTC timestamp format |
| **payload** | Map (`M`) | Contains `{ "user_id": ..., "event": "Status", "type": <status_text> }` |

## 2. Keyword Fuzzy Resolution Map

The client-side parser maps custom strings to canonical filenames using substring match checking:

| Input Text Pattern | Resolved Filename Suffix | Mapped Image Asset Path |
| :--- | :--- | :--- |
| `"sleep"`, `"nap"`, `"bed"` | `"sleeping"` | `/<camper>_status/<camper>_sleeping.jpg` |
| `"drink"`, `"beer"`, `"pub"`, `"pint"` | `"drinking"` | `/<camper>_status/<camper>_drinking.jpg` |
| `"eat"`, `"food"`, `"dinner"`, `"lunch"` | `"eating"` | `/<camper>_status/<camper>_eating.jpg` |
| `"wet"`, `"toilet"`, `"pee"`, `"poo"` | `"wet"` | `/<camper>_status/<camper>_wet.jpg` |
| `"lecture"`, `"talk"`, `"stage"` | `"lecture"` | `/<camper>_status/<camper>_lecture.jpg` |
| `"workshop"`, `"lab"`, `"coding"`, `"code"`| `"workshop"` | `/<camper>_status/<camper>_workshop.jpg` |
| `"roam"`, `"walk"`, `"step"`, `"tent"` | `"roaming"` | `/<camper>_status/<camper>_roaming.jpg` |
| `"tire"`, `"exhaust"`, `"weary"` | `"tired"` | `/<camper>_status/<camper>_tired.jpg` |
| `"chill"`, `"relax"`, `"rest"` | `"chilling"` | `/<camper>_status/<camper>_chilling.jpg` |
| `"annoy"`, `"mad"`, `"angry"`, `"sad"` | `"annoyed"` | `/<camper>_status/<camper>_annoyed.jpg` |
| *Otherwise / No Match* | `"normal"` | `/<camper>_status/<camper>_normal.jpg` |
