# Data Model: Additional Drinks Tracking

This document details the extension of the database record schema (for both the local JSON database and AWS DynamoDB partitions) to support the new beverage categories: `Martini`, `G+T`, `Negroni`, and `Port`.

---

## 1. Updated Single-Table Key Mappings

The existing single-table primary key mappings are fully preserved. No new keys are added, maintaining compliance with core Principle IV (Safe and Secure Database Modeling).

| Partition Key (`event`) | Sort Key (`type`) | Purpose |
| :--- | :--- | :--- |
| `camper#aggregates#<user_id>` | `totals` | Caches the aggregate counts and beverage tallies for an individual camper. |
| `camper#aggregates#combined` | `totals` | Caches the summed totals and rankings across all campers. |

---

## 2. Updated Record Schemas

The `categories` object map inside the aggregate records is updated to support the new beverage keys. 

### A. Individual Camper Aggregates Record (`camper#aggregates#<user_id>`)
* **Partition Key (`event`)**: `camper#aggregates#cha`
* **Sort Key (`type`)**: `totals`

```json
{
  "event": "camper#aggregates#cha",
  "type": "totals",
  "user_id": "cha",
  "last_updated": "2026-07-15T16:00:00Z",
  "categories": {
    "Water": 3,
    "Coffee": 2,
    "Tea": 1,
    "Soft": 0,
    "Lager": 4,
    "IPA": 2,
    "Cider": 1,
    "Ale": 0,
    "Martini": 2,
    "G+T": 3,
    "Negroni": 4,
    "Port": 1
  },
  "total_drinks": 18,
  "beer_drinks": 7
}
```

*Note on calculation:* 
* `total_drinks` is the sum of ALL drinks logged (Water, Coffee, Tea, Soft, Lager, IPA, Cider, Ale, Martini, G+T, Negroni, Port).
* `beer_drinks` is strictly the sum of `Lager`, `IPA`, `Cider`, and `Ale` subset categories. The newly added spirit drinks do not count towards the beer subset.

### B. Combined Aggregates Record (`camper#aggregates#combined`)
* **Partition Key (`event`)**: `camper#aggregates#combined`
* **Sort Key (`type`)**: `totals`

The combined aggregates record aggregates all drink categories across all active campers.

```json
{
  "event": "camper#aggregates#combined",
  "type": "totals",
  "user_id": "combined",
  "last_updated": "2026-07-15T16:05:00Z",
  "categories": {
    "Water": 25,
    "Lager": 32,
    "Martini": 6,
    "G+T": 12,
    "Negroni": 15,
    "Port": 5
  },
  "total_drinks": 95,
  "beer_drinks": 32,
  "leaderboard": [
    { "user_id": "cha", "display_name": "Charlotte", "total_drinks": 18 },
    { "user_id": "hvy", "display_name": "Harvy", "total_drinks": 15 }
  ]
}
```
