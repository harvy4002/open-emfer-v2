# Data Model: Participant Admin Portal

This document describes the structure of data processed, fetched, and cached by the Participant Admin Portal.

## 1. Remote Data Models (DynamoDB Keys)

The admin portal interacts with the single-table DynamoDB structure under the following partition and sort keys:

### Camper Aggregates
- **Key Schema**: Partition Key = `camper#aggregates#<user_id>` (e.g. `camper#aggregates#ali`), Sort Key = `totals`
- **JSON Structure**:
  ```json
  {
    "user_id": "ali",
    "total_drinks": 12,
    "beer_drinks": 8,
    "categories": {
      "Lager": 6,
      "IPA": 2,
      "Water": 3,
      "Pee": 4,
      "Poo": 1,
      "Start": 2,
      "Stop": 2
    }
  }
  ```
- **Validation**: Metric counts inside `categories` and totals MUST be non-negative integers (floor bounded at `0`).

### Device State (Steps Telemetry)
- **Key Schema**: Partition Key = `device#eui-70b3d57ed0051111#<user_id>`, Sort Key = `state`
- **JSON Structure**:
  ```json
  {
    "cumulative_steps": 14500,
    "cumulative_distance_km": 10.45,
    "last_known_latitude": 52.041118,
    "last_known_longitude": -2.377757,
    "last_known_timestamp": "2026-07-12T14:30:22Z"
  }
  ```

---

## 2. Browser Local Storage Schema

The admin dashboard uses browser-native `localStorage` to persist configuration and session authentication state across browser instances without requiring cookies or dynamic servers.

### Caching Schemas

| LocalStorage Key | Data Type | Description |
|------------------|-----------|-------------|
| `admin_tracker_key` | Plain String | The shared secret `tracker_key` loaded in authorization headers. |
| `active_user_id` | Plain String | The active locked user shortcode (e.g. `ali`, `hvy`, `bob`) bound to submissions. |

### Client Session State (JavaScript Memory)
At runtime, the browser maintains a reactive, localized state model:
```javascript
let appState = {
  activeUser: "ali",            // String: hvy, ali, or bob
  trackerKey: "...",            // String: Authorization secret token
  submitLocked: false,          // Boolean: Double-tap throttle flag
  counts: {                     // Object: Dynamically loaded current metrics
    total_drinks: 0,
    beer_drinks: 0,
    categories: {}
  },
  steps: 0                      // Integer: Current steps count from /history
};
```
