# Data Model: Multi-User Tracking

This document details the extensions to the DynamoDB single-table schema and browser local storage schemas to isolate multi-user datasets while keeping read latency low.

---

## 1. Updated Single-Table Key Mappings

The DynamoDB composite primary key system is expanded to inject the compact `user_id` identifier into the Partition Keys (`event`).

| Domain | Partition Key (`event`) | Sort Key (`type`) | Purpose |
| :--- | :--- | :--- | :--- |
| **Camper Raw Logs** | `camper#logs#<user_id>` | `raw#<timestamp>#<uuid>` | Isolated historical log events for a specific camper. |
| **Individual Aggregates**| `camper#aggregates#<user_id>` | `totals` | Singleton state caching overall sums for a specific camper. |
| **Combined Aggregates** | `camper#aggregates#combined`| `totals` | Singleton state caching sums across *all* campers. |
| **T1000 Telemetry** | `device#<device_id>#<user_id>` | `telemetry#<timestamp>` | Historical record of GPS, isolated to the camper owning the device. |
| **Device State** | `device#<device_id>#<user_id>` | `state` | Isolated current coordinates and history arrays (max 20 entries). |

---

## 2. Record Schemas

### A. Individual Camper Aggregates Singleton
* **Partition Key (`event`)**: `camper#aggregates#ali`
* **Sort Key (`type`)**: `totals`

```json
{
  "event": "camper#aggregates#ali",
  "type": "totals",
  "user_id": "ali",
  "display_name": "Alice",
  "last_updated": "2026-07-10T12:05:00Z",
  "categories": {
    "Lager": 5,
    "Water": 3,
    "toilet_visits": 2
  },
  "total_drinks": 8,
  "beer_drinks": 5
}
```

---

### B. Combined Aggregates Singleton
* **Partition Key (`event`)**: `camper#aggregates#combined`
* **Sort Key (`type`)**: `totals`

```json
{
  "event": "camper#aggregates#combined",
  "type": "totals",
  "user_id": "combined",
  "last_updated": "2026-07-10T12:06:00Z",
  "categories": {
    "Lager": 45,
    "Water": 22,
    "toilet_visits": 12
  },
  "total_drinks": 67,
  "beer_drinks": 45,
  "leaderboard": [
    { "user_id": "hvy", "display_name": "Harvy", "total_drinks": 40 },
    { "user_id": "ali", "display_name": "Alice", "total_drinks": 27 }
  ]
}
```

*(Note: The `leaderboard` array allows the frontend to easily map user rankings on the combined screen.)*

---

## 3. LocalStorage Extension

The browser `localStorage` schema is expanded to retain the active user's short identifier, allowing them to drop the URL parameter if desired after first load.

### `active_user_context` (JSON String)
```json
{
  "user_id": "ali",
  "display_name": "Alice"
}
```
*(If empty or null, defaults to `hvy`)*
