# Data Model: All-Time Leaderboard Steps and Daily Resets

This document details the extensions to the singleton database aggregate records to support automated daily resets and persistent, all-time cumulative counters.

---

## 1. Updated Aggregate Record Schema (`camper#aggregates#<user_id>`)

Each camper's individual totals record is extended to track both daily active totals and cumulative all-time totals.

* **Partition Key (`event`)**: `camper#aggregates#cha`
* **Sort Key (`type`)**: `totals`

```json
{
  "event": "camper#aggregates#cha",
  "type": "totals",
  "user_id": "cha",
  "last_updated": "2026-07-15T16:00:00Z",
  "last_reset_date": "2026-07-15",
  "categories": {
    "Water": 3,
    "Lager": 4
  },
  "total_drinks": 7,
  "beer_drinks": 4,
  "all_time_total_drinks": 42,
  "all_time_cumulative_steps": 125000
}
```

*Note on behaviors:*
* **On Daily Reset**: When the calendar date UTC transitions, `total_drinks`, `beer_drinks`, and the `categories` map are reset to 0/empty. However, `all_time_total_drinks` and `all_time_cumulative_steps` remain **untouched** and accumulate persistently across all days.
* **`last_reset_date`**: Records the date string (YYYY-MM-DD UTC) of the most recent reset, helping the lazy-evaluation trigger detect transitions.

---

## 2. Updated Combined Record Schema (`camper#aggregates#combined`)

The combined aggregates singleton tracks all-time rankings for both beverages and physical steps.

* **Partition Key (`event`)**: `camper#aggregates#combined`
* **Sort Key (`type`)**: `totals`

```json
{
  "event": "camper#aggregates#combined",
  "type": "totals",
  "user_id": "combined",
  "last_updated": "2026-07-15T16:05:00Z",
  "total_drinks": 95,
  "beer_drinks": 32,
  "categories": {
    "Water": 25,
    "Lager": 32
  },
  "leaderboard": [
    { "user_id": "cha", "display_name": "Charlotte", "all_time_drinks": 42 },
    { "user_id": "hvy", "display_name": "Harvy", "all_time_drinks": 30 }
  ],
  "steps_leaderboard": [
    { "user_id": "hvy", "display_name": "Harvy", "all_time_steps": 150000 },
    { "user_id": "cha", "display_name": "Charlotte", "all_time_steps": 125000 }
  ]
}
```
