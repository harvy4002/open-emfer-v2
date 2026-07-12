# Data Model: Open EMF Camper API

This document details the single-table DynamoDB layout and composite-key mappings used to store camper telemetry, bank transactions, and IoT metrics.

---

## 1. Unified Primary Key Mappings

All endpoints write to a single DynamoDB table. The records are structured using Partition Key (`event`) and Sort Key (`type`) to isolate different domains:

| Domain | Partition Key (`event`) | Sort Key (`type`) | Purpose |
| :--- | :--- | :--- | :--- |
| **Camper Raw Logs** | `camper#logs` | `raw#<timestamp>#<uuid>` | Historical immutable record of logged events (drinks, status, reset). |
| **Camper Aggregates** | `camper#aggregates` | `totals` | Singleton state caching overall sums across all logging categories. |
| **T1000 Telemetry** | `device#<device_id>` | `telemetry#<timestamp>` | Historical record of T1000 GPS, temperature, and light levels. |
| **Device State** | `device#<device_id>` | `state` | Current coordinates, location history array (max 20 entries), and last valid lock. |
| **Monzo Sync** | `monzo#transactions` | `latest` | Cache of formatted credit/debit transactions and total campaign expenditure. |

---

## 2. Item Schemas

### A. Camper Raw Log
* **Partition Key (`event`)**: `camper#logs`
* **Sort Key (`type`)**: `raw#2026-07-10T12:00:00Z#8f3a2b7c-ef92-410a-8105-06d28f4277bc`

```json
{
  "event": "camper#logs",
  "type": "raw#2026-07-10T12:00:00Z#8f3a2b7c-ef92-410a-8105-06d28f4277bc",
  "category": "Drinks" | "Status" | "Activity",
  "name": "Lager" | "Chilling" | "Lecture",
  "timestamp": "2026-07-10T12:00:00Z",
  "beer": true,
  "reverse": false,
  "tracker_key": "valid-hashed-key"
}
```

---

### B. Camper Aggregates Singleton
* **Partition Key (`event`)**: `camper#aggregates`
* **Sort Key (`type`)**: `totals`

```json
{
  "event": "camper#aggregates",
  "type": "totals",
  "last_updated": "2026-07-10T12:05:00Z",
  "categories": {
    "Lager": 15,
    "IPA": 4,
    "Water": 12,
    "Coffee": 6,
    "toilet_visits": 5,
    "gaming_seconds": 1800
  },
  "total_drinks": 37,
  "beer_drinks": 19
}
```

---

### C. Device State Singleton (T1000)
* **Partition Key (`event`)**: `device#eui-70b3d57ed0051111`
* **Sort Key (`type`)**: `state`

```json
{
  "event": "device#eui-70b3d57ed0051111",
  "type": "state",
  "device_id": "eui-70b3d57ed0051111",
  "device_type": "T1000",
  "last_updated": "2026-07-10T12:00:00Z",
  "last_known_latitude": 51.5074,
  "last_known_longitude": -0.1278,
  "last_known_timestamp": "2026-07-10T12:00:00Z",
  "cumulative_distance_km": 1.25,
  "cumulative_steps": 1984,
  "location_history": [
    { "lat": 51.5074, "lng": -0.1278, "time": "2026-07-10T12:00:00Z" }
  ]
}
```

---

### D. Monzo Transactions Cache
* **Partition Key (`event`)**: `monzo#transactions`
* **Sort Key (`type`)**: `latest`

```json
{
  "event": "monzo#transactions",
  "type": "latest",
  "last_sync": "2026-07-10T12:30:00Z",
  "total_expenditure_gbp": 84.50,
  "transactions": [
    {
      "id": "tx_00001Z",
      "description": "EMF Camp Bar",
      "amount_gbp": -4.50,
      "timestamp": "2026-07-10T12:15:00Z"
    },
    {
      "id": "tx_00002Z",
      "description": "(CREDIT) Cash Deposit",
      "amount_gbp": 20.00,
      "timestamp": "2026-07-10T11:00:00Z"
    }
  ]
}
```
