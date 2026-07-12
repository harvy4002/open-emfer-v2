# Data Model: Local Developer Simulator

This document details the schema of the local file-based database (`web/web_local_db.json`) used to emulate the DynamoDB single-table environment offline.

---

## 1. Local JSON Database Structure (`web/web_local_db.json`)

The local JSON database operates as a single unified dictionary of keys. Each top-level dictionary key represents a simulated **Partition Key** (`event`), and the nested sub-keys map to the **Sort Key** (`type`), providing an identical structure to the DynamoDB tables.

### Complete DB Schema Definition:
```json
{
  "camper#aggregates#combined": {
    "totals": {
      "user_id": "combined",
      "total_drinks": 25,
      "beer_drinks": 12,
      "categories": {
        "Lager": 12,
        "Water": 8,
        "Coffee": 5
      },
      "leaderboard": [
        { "user_id": "hvy", "display_name": "Harvy", "total_drinks": 15 },
        { "user_id": "ali", "display_name": "Alice", "total_drinks": 10 }
      ]
    }
  },
  "camper#aggregates#ali": {
    "totals": {
      "user_id": "ali",
      "display_name": "Alice",
      "total_drinks": 10,
      "beer_drinks": 4,
      "categories": {
        "Lager": 4,
        "Water": 6
      }
    }
  },
  "device#eui-70b3d57ed0051111#ali": {
    "state": {
      "last_known_latitude": 51.5074,
      "last_known_longitude": -0.1278,
      "last_known_timestamp": "2026-07-10T12:00:00Z",
      "cumulative_distance_km": 0.0,
      "cumulative_steps": 0,
      "location_history": []
    }
  },
  "monzo#transactions": {
    "latest": {
      "total_expenditure_gbp": 45.50,
      "transactions": [
        {
          "id": "tx_local01",
          "description": "EMF Camp Food stall",
          "amount_gbp": -12.50,
          "timestamp": "2026-07-10T12:10:00Z"
        }
      ]
    }
  }
}
```

---

## 2. In-Memory Playground State

Inside `web/js/simulator.js`, the local playground maintains simple input telemetry parameters prior to posting:

```javascript
const playgroundState = {
  active_user: "ali",
  t1000: {
    lat: 51.5074,
    lng: -0.1278,
    temp: 24.5,
    light: 150
  },
  browan: {
    sound_level: 45.2
  },
  monzo: {
    amount: -5.00,
    merchant: "Camp Bar"
  }
};
```
