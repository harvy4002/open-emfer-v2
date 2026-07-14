# Quickstart Validation Guide: Event Sourcing for Telemetry and Aggregates

This guide verifies the generation of immutable event logs and the successful in-memory aggregate state reconstruction of the playback endpoint.

## Prerequisites
Run the backend API emulator in a background terminal:
```bash
python3 backend/sim_server.py
```

## Scenario 1: Validate Immutable Event Appends

1. Clear the local database cache if needed (`rm web/web_local_db.json`).
2. Submit a sequenced set of events for `cha` across simulated time jumps (this test leverages consecutive standard POSTs, assuming chronological execution):
   ```bash
   # Log a Coffee
   curl -X POST http://localhost:3000/beer -H "tracker_key: cha-mock-secret-key" -H "Content-Type: application/json" -d '{"user_id": "cha", "event": "Drinks", "type": "Coffee"}'
   
   sleep 2
   
   # Log a Lager
   curl -X POST http://localhost:3000/beer -H "tracker_key: cha-mock-secret-key" -H "Content-Type: application/json" -d '{"user_id": "cha", "event": "Drinks", "type": "Lager", "beer": true}'
   ```
3. Inspect `web/web_local_db.json`. Verify that under the `"camper#events#cha"` root object, there are exactly two distinct child keys prefixed with `"event#..."` corresponding to the two actions, preserving the exact payloads. Verify `"camper#aggregates#cha"` -> `"totals"` reflects `total_drinks: 2`.

## Scenario 2: Validate Time-Bounded Playback Reconstruction

1. Choose a timestamp chronologically *between* the two events recorded above (e.g., if event 1 happened at `12:00:01` and event 2 at `12:00:03`, select `12:00:02`).
2. Execute the playback query boundary constraint:
   ```bash
   curl "http://localhost:3000/playback?user_id=cha&until=2026-07-13T12:00:02Z"
   ```
3. **Verify** that the returned JSON payload successfully isolates and plays back only the first event:
   * `total_drinks` equals exactly `1`.
   * `events_processed` equals `1`.
   * The `Lager` category does not exist in the reconstructed state map.
