# Quickstart Guide: Sensecap Location Map Integration

This guide provides runnable instructions to locally test and validate the end-to-end Sensecap location mapping integration.

## 1. Prerequisites
- **Local Dev Server**: Ensure the simulated server is running locally (e.g., via `python backend/sim_server.py`).
- **Web Browser**: Open the local dashboard (`web/index.html`) or simulator (`web/simulator.html`).

---

## 2. End-to-End Validation Scenario

This scenario injects location coordinates covering a 4-hour period to verify that only coordinates within the last 3 hours of the latest coordinate's timestamp are rendered on the map.

### Step 1: Start the Local Simulation Server
Explain/run the server start command:
```bash
python backend/sim_server.py
```

### Step 2: Inject Test Coordinate Telemetry (POST)
Send a sequence of coordinate payloads using `curl` representing a path walked. Notice that the first coordinate is **more than 3 hours older** than the latest point and should be filtered out by the dashboard map.

Assume the secure `tracker_key` header token is `test_key` (check local configuration in `backend/sim_server.py`).

```bash
# 1. 4 Hours Ago (Should be filtered out)
curl -X POST http://localhost:8080/sensecap \
  -H "Content-Type: application/json" \
  -H "tracker_key: test_key" \
  -d '{"device_id": "device#eui-70b3d57ed0051111#hvy", "timestamp": "2026-07-14T11:00:00Z", "latitude": 52.0401, "longitude": -2.3760, "temperature": 21.0, "light": 100}'

# 2. 2.5 Hours Ago (Should render)
curl -X POST http://localhost:8080/sensecap \
  -H "Content-Type: application/json" \
  -H "tracker_key: test_key" \
  -d '{"device_id": "device#eui-70b3d57ed0051111#hvy", "timestamp": "2026-07-14T12:30:00Z", "latitude": 52.0411, "longitude": -2.3780, "temperature": 22.0, "light": 150}'

# 3. 1 Hour Ago (Should render)
curl -X POST http://localhost:8080/sensecap \
  -H "Content-Type: application/json" \
  -H "tracker_key: test_key" \
  -d '{"device_id": "device#eui-70b3d57ed0051111#hvy", "timestamp": "2026-07-14T14:00:00Z", "latitude": 52.0418, "longitude": -2.3790, "temperature": 23.0, "light": 180}'

# 4. Now/Latest Coordinate (Should render as the active head marker)
curl -X POST http://localhost:8080/sensecap \
  -H "Content-Type: application/json" \
  -H "tracker_key: test_key" \
  -d '{"device_id": "device#eui-70b3d57ed0051111#hvy", "timestamp": "2026-07-14T15:00:00Z", "latitude": 52.0425, "longitude": -2.3800, "temperature": 22.5, "light": 200}'
```

### Step 3: Fetch the Location History (GET)
Verify that the simulation database lists all 4 coordinates successfully:
```bash
curl "http://localhost:8080/history?user_id=hvy"
```

### Step 4: Verify the Public Dashboard Map (Visual Verification)
1. Open the public dashboard `web/index.html?u=hvy` in your browser.
2. Observe the interactive **Camper Location History Map (T1000 Trail)**.
3. **Expected Rendering Outcome**:
   - The map centers near `52.0411, -2.3784` using standard EMF Camp styled map tiles.
   - Exactly **3 location points** are plotted (the coordinate at `12:30`, `14:00`, and `15:00`).
   - The point at `11:00` (4 hours older than the latest coordinate of `15:00`) **is excluded** from the trail map and markers.
   - The latest coordinate (`15:00`) has a distinguished, larger red pulsing marker representing the active position.
   - Hovering or clicking on markers displays their timestamp and cumulative telemetry metrics.
