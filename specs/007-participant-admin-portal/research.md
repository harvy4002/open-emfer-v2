# Technical Research: Participant Admin Portal

## Decisions & Technical Architecture

### 1. Reversal API Integration
- **Decision**: Leverage the existing `POST /beer` endpoint, passing `"reverse": true` in the JSON request payload to decrement numerical counts.
- **Rationale**: The backend simulator (`backend/sim_server.py`) and standard lambda handlers already natively support the `"reverse": true` parameter inside the standard `TelemetryPostPayload` schema. When `reverse` is set to `true`, the value offset is evaluated as `-1` instead of `+1`, decrementing the associated metric down to a minimum floor of `0`.
- **Alternatives Considered**: Creating separate `/beer/reverse` or `/toilet/reverse` REST paths. Rejected because using the unified `POST /beer` with a `reverse: true` flag is already implemented, fully documented in `openapi.json`, and avoids introducing unnecessary API routes or Lambdas.

### 2. Live Value Display & Synchronization
- **Decision**: Fetch the camper's active state from `GET /beer?user_id=<user_id>` and `GET /history?user_id=<user_id>` on page load, displaying current counts adjacent to their respective item controls in the admin dashboard. Provide a manual "Sync" refresh button to pull the latest state on demand.
- **Rationale**: Keeps the camper informed about their active database counts without needing to open the public-facing Grafana dashboard.
- **Alternatives Considered**: Real-time WebSockets. Rejected as too complex and battery-draining for campground mobile devices. The low-friction, on-load REST GET fetch combined with instant local cache updates and a manual sync button satisfies all requirements with near-zero latency and high network efficiency.

### 3. Isolated Admin URLs & Link Context Locking
- **Decision**: Parse the `u` (or `user_id`) query parameter from the URL on load (e.g., `/admin.html?u=ali`), and lock the session strictly to that camper profile. Completely hide or remove the shared profile selector dropdown from the active panels to guarantee isolation.
- **Rationale**: Enforces a strict one-link-per-user model, preventing campers from accidentally logging metrics to other participants' accounts under outdoor, fast-paced field conditions.
- **Alternatives Considered**: A password-protected profile switcher. Rejected as too high-friction for simple, single-handed campsite logging. Individual bookmarkable links provide the perfect balance of security, speed, and error prevention.

---

## Technical Specifications & Variables

- **Backend Telemetry Endpoint**: `POST /beer`
- **Backend Fetch Endpoints**: 
  - `GET /beer?user_id=<user_id>` (for Drinks, Toilet, and general categories)
  - `GET /history?user_id=<user_id>` (for Steps telemetry)
- **Hardcoded Shortcodes**:
  - `hvy` -> Harvy Atwal
  - `ali` -> Alice Smith
  - `bob` -> Bob Camper
- **Security Authorization Header**: `tracker_key` (supplied via standard text prompt, saved locally in `localStorage` as `admin_tracker_key`).
