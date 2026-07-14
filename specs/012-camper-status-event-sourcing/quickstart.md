# Quickstart Validation Guide: Event-Sourced Camper Status Image Matching

This guide outlines runnable verification scenarios to prove that camper status updates match the explicitly logged clicks, completely ignoring implicit sensor telemetries.

## Prerequisites
Ensure the local frontend assets are served statically:
```bash
python3 backend/sim_server.py
```

## Scenario 1: Validate Explicit Only Filtering

1. Set Charlotte's initial status to **Sleeping** (explicit status):
   ```bash
   curl -X POST http://localhost:3000/beer -H "tracker_key: cha-mock-secret-key" -H "Content-Type: application/json" -d '{"user_id": "cha", "event": "Status", "type": "Sleeping"}'
   ```
2. Log an implicit steps event:
   ```bash
   curl -X POST http://localhost:3000/steps -H "tracker_key: cha-mock-secret-key" -H "Content-Type: application/json" -d '{"user_id": "cha", "steps": 500}'
   ```
3. Query Charlotte's active status:
   ```bash
   curl -s "http://localhost:3000/beer?event=status&type=latest&user_id=cha"
   ```
4. **Verify** that the returned status is strictly **`sleeping`**, completely ignoring the intermediate implicit step log!

## Scenario 2: Validate Fuzzy Keyword Image Resolution

1. Open Charlotte's dashboard:
   [http://localhost:3000/index.html?u=cha](http://localhost:3000/index.html?u=cha)
2. Log a custom status of **"Coding"** from the admin portal:
   ```bash
   curl -X POST http://localhost:3000/beer -H "tracker_key: cha-mock-secret-key" -H "Content-Type: application/json" -d '{"user_id": "cha", "event": "Status", "type": "Coding"}'
   ```
3. **Verify** that:
   * The status badge resolves successfully.
   * The visual profile photo updates to display Charlotte's `/cha_status/cha_workshop.jpg` asset (mapped from "Coding").
