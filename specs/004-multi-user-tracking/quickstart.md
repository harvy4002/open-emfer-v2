# Quickstart Validation Guide: Multi-User Tracking

This guide outlines steps to verify the multi-user isolation, dual-write aggregations, and QR-optimized client-side bindings.

---

## Prerequisites & Setup

1. **Local Test Environment**: Ensure you have Python 3.12+ installed.
2. **Dependencies**: Install development and testing dependencies:
   ```bash
   pip install pytest moto boto3
   ```
3. **Local Frontend Server**:
   Execute a simple Python server mapping the static assets folder `web/`:
   ```bash
   python3 -m http.server -d web 8080
   ```

---

## Validation Scenario 1: Isolated Admin Logging (Dual-Write)

Verifies that passing a `user_id` query parameter isolates the write to the specific user while updating the combined aggregate partition simultaneously.

### Execute Command (Mock HTTP POST)
```bash
curl -X POST https://api.camper.local/beer \
  -H "Authorization: mock-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "ali",
    "event": "Drinks",
    "type": "Lager"
  }'
```

### Expected Outcome
- **Response Code**: `201 Created`
- **Response Body**:
  ```json
  {
    "status": "success",
    "user_id": "ali",
    "category": "Drinks",
    "name": "Lager",
    "beer": true
  }
  ```
- **DynamoDB Verification**:
  - `camper#aggregates#ali` partition shows `"Lager": 1`.
  - `camper#aggregates#combined` partition shows `"Lager"` incremented by 1 globally.

---

## Validation Scenario 2: QR URL Resolution & Binding

Verifies that loading the public dashboard with a short identifier (e.g., `?u=ali`) instantly binds the frontend fetch requests and updates the local storage.

### Interaction Steps
1. Open `http://localhost:8080/index.html?u=ali` in your browser.
2. Verify the heading reads "Alice's Dashboard" (or equivalent resolving of `ali`).
3. Open your browser console (F12) and inspect the Network tab.
4. Verify the frontend makes a `GET` request to `https://api.camper.local/beer?user_id=ali`.
5. Open Developer Tools → Application → Local Storage, and verify `active_user_context` shows `{"user_id": "ali"}`.

---

## Validation Scenario 3: Combined Dashboard Leaderboard

Verifies that the `combined` query triggers the combined aggregate view.

### Interaction Steps
1. Open `http://localhost:8080/index.html?u=combined` in your browser.
2. Verify that environmental charts (Temperature, Light) are hidden (as specified in Option A).
3. Verify that the metrics tiles show the global accumulated numbers.
4. Verify that the UI renders the sorted array of the `leaderboard` property returned from the `combined` endpoint.
