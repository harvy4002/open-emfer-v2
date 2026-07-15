# Quickstart Validation Guide: All-Time Leaderboards and Daily Resets

This guide outlines step-by-step instructions to validate the lazy daily reset mechanics, raw event store persistence, and all-time leaderboard rankings on the combined view.

## Prerequisites
Ensure the local frontend assets are served statically, and that the backend simulator is active:
```bash
# Start the local backend simulator & static server on port 3000
python3 backend/sim_server.py
```

---

## Scenario 1: Validate Automatic Daily Reset and Historical Event Retention

1. Clear the simulator database or start with a clean state.
2. Log a beverage for Harvy:
   ```bash
   curl -X POST http://localhost:3000/beer \
     -H "Content-Type: application/json" \
     -H "tracker_key: mock-super-secret-key" \
     -d '{"user_id": "hvy", "event": "Drinks", "type": "Water"}'
   ```
3. Verify his totals:
   * **Total Drinks**: 1
   * **All-Time Total Drinks**: 1
4. Now, to test a lazy calendar-day transition, modify the `last_updated` or `last_reset_date` of Harvy's totals in `web/web_local_db.json` (or set the calendar date to a mock string representing yesterday, e.g., `"last_reset_date": "2026-07-14"`).
5. Post another beverage log for Harvy.
6. Verify that on processing the request:
   * The simulator detects the date mismatch (`2026-07-14` vs today's date).
   * It appends a `ResetDay` event to the raw event list.
   * It resets Harvy's daily active `total_drinks` to `1` (from the new log action).
   * It increments Harvy's `all_time_total_drinks` to `2` (the persistent accumulator is untouched).
7. Validate that querying `/playback?user_id=hvy` correctly processes and returns both raw beverage logs, proving raw event retention is fully preserved.

---

## Scenario 2: Validate All-Time Step Leaderboard on Combined Screen

1. Open your browser and navigate to the Combined dashboard:
   [http://localhost:3000/index.html?u=combined](http://localhost:3000/index.html?u=combined)
2. Open your terminal and simulate posting steps for Charlotte:
   ```bash
   curl -X POST http://localhost:3000/steps \
     -H "Content-Type: application/json" \
     -H "tracker_key: cha_k_1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d" \
     -d '{"user_id": "cha", "steps": 12000}'
   ```
3. Simulate posting steps for Ash:
   ```bash
   curl -X POST http://localhost:3000/steps \
     -H "Content-Type: application/json" \
     -H "tracker_key: ash_k_9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c" \
     -d '{"user_id": "ash", "steps": 8500}'
   ```
4. Return to the browser tab. On the combined dashboard, verify that under the **All-Time Steps Leaderboard** section:
   * **Charlotte** is ranked first with 12,000 steps.
   * **Ash** is ranked second with 8,500 steps.
