# Quickstart Validation Guide: Local Developer Simulator

This guide describes how to start the local developer server and API simulator to manually verify end-to-end data flows offline.

---

## 1. Starting the Servers

Open two terminal tabs on your workstation:

### Terminal Tab 1: Run local dashboards website (Port 8080)
```bash
python3 -m http.server -d web 8080
```

### Terminal Tab 2: Run local mock API server (Port 3000)
```bash
python3 backend/sim_server.py
```

---

## 2. Interactive Ingestion Flow Scenarios

### Scenario A: Load the Playground
1. Navigate your web browser to `http://localhost:8080/simulator.html`.
2. Verify the playground dashboard renders and establishes a websocket/polling connection with `localhost:3000`.

### Scenario B: Inject T1000 GPS coordinates
1. On the "T1000 Ingest" card form, enter custom coordinate metrics:
   * **Latitude**: `51.5074`
   * **Longitude**: `-0.1278`
2. Click **Inject Telemetry Payload**.
3. Verify that the playground's Console Log inspector outputs:
   * `>> POST /sensecap HTTP/1.1 (201 Created)`
   * The exact submitted request JSON dictionary.
4. Load the camper's public dashboard `http://localhost:8080/index.html?u=ali` in another browser tab, and confirm that the coordinates map point is drawn instantly.

### Scenario C: Trigger Monzo Sync
1. On the "Monzo Bank Sync" card, click the **Simulate Cron Sync** button.
2. Confirm that the local `sim_server.py` console terminal prints a request trace, reads/updates `web_local_db.json`, and appends a `(CREDIT)` transaction to the cached listings.
3. Open `http://localhost:8080/index.html` and verify the camp expenses counter has been updated.
