# Quickstart Validation Guide: Participant Admin Portal

This guide provides step-by-step instructions to run the local simulation environment and verify the end-to-end telemetry logging, display, and reversal logic in the Participant Admin Portal.

---

## 1. Prerequisites & Setup

Ensure you have Python 3.12+ installed.

1. **Start the Local API & Assets Server**:
   From the project root, run the simulation server which hosts the REST endpoints on port `3000` and serves the static frontend assets on port `8080`:
   ```bash
   python backend/sim_server.py
   ```
   *Expected Output*:
   ```text
   Local simulation server started!
   - Static Web Server: http://localhost:8080
   - Mock API Gateway: http://localhost:3000
   ```

2. **Open the Locked Admin Page**:
   Open your browser and navigate to Alice's personalized, locked admin link:
   [http://localhost:8080/admin.html?u=ali](http://localhost:8080/admin.html?u=ali)

3. **Authenticate**:
   - The portal will prompt you for the `tracker_key`.
   - Input: `"mock-super-secret-key"` and click Save.
   - Verify that the key is stored in `localStorage` under `admin_tracker_key`.

---

## 2. Validation Scenarios

### Validation Scenario 1: Initial State Display
- **Steps**:
  1. Load [http://localhost:8080/admin.html?u=ali](http://localhost:8080/admin.html?u=ali).
  2. Verify that the page header shows **Alice Smith's Logging Portal** (resolving `ali` from `Assumption 4`).
  3. Verify that the profile switcher dropdown is **hidden** or disabled (FR-007).
  4. Inspect the "Drinks" and "Toilet" categories. Each item should display its active database count next to the label (fetched via `GET /beer?user_id=ali`).

---

### Validation Scenario 2: Tactile Counter Addition ("+")
- **Steps**:
  1. Locate "Lager" under the Drinks panel.
  2. Click the **"+" button** next to "Lager".
  3. Verify that:
     - The buttons disable briefly for `500ms` (FR-005) to prevent double-tap submissions.
     - A secure `POST /beer` request is dispatched to the Mock API with `{ "user_id": "ali", "event": "Drinks", "type": "Lager", "beer": true, "reverse": false }` (referenced in [Contracts](./contracts/beer-post.json)).
     - The displayed count for Lager increments by `1` (e.g., from `0` to `1`).
     - A green success banner flashes: `Success: logged Lager for ALI`.

---

### Validation Scenario 3: Tactile Counter Reversal ("-")
- **Steps**:
  1. Click the **"-" button** next to "Lager" (which currently displays a count of `1`).
  2. Verify that:
     - Submissions lock for `500ms`.
     - A secure `POST /beer` request is dispatched with `"reverse": true` in the JSON body.
     - The displayed count decrements back by `1` (e.g., from `1` to `0`).
     - A green success banner flashes: `Success: logged Lager (REVERSED) for ALI`.

---

### Validation Scenario 4: Floor Bound Protection & LOCK
- **Steps**:
  1. Verify the count next to "Lager" is `0`.
  2. Look at the **"-" button** next to "Lager".
  3. Verify that the **"-" button is disabled / locked** (FR-012) and cannot be clicked.
  4. Attempt to trigger a reverse request (e.g. via direct script interaction or testing manual fetch) and verify that the backend or client rejects/ignores the submission, maintaining a floor boundary of `0`.
