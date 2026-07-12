# Technical Research: Local Developer Simulator

This document outlines the lightweight local server designs, CORS preflight interception mechanics, and local JSON database file synchronizations chosen to implement our development simulator.

---

## 1. Zero-Dependency Python HTTP Emulation (`BaseHTTPRequestHandler`)

### Decision
Utilize Python's built-in standard library module `http.server.BaseHTTPRequestHandler` to implement the mock API server (`sim_server.py`). The script will listen on local port 3000, inspect `self.path` and `self.command`, and route requests to mock route handler methods.

### Rationale
- **Immediate Setup Compliance (Principle VIII)**: Using standard libraries eliminates the requirement to run `pip install` or configure python virtual environments (venv) on the developer's host machine. The simulator runs out-of-the-box instantly on any workstation with Python 3.
- **Cold-Start Elimination**: Native standard library sockets boot in milliseconds, providing an ultra-responsive feedback loop.

### Alternatives Considered
- **Flask / FastAPI / Express**: Rejected. Although Flask/FastAPI simplify routing, requiring third-party library installations violates our zero-dependency constraints and introduces dependency installation friction for developers.

---

## 2. CORS Preflight Interception & Wildcard Injection

### Decision
The Python API simulator server will explicitly intercept incoming `OPTIONS` HTTP requests on all paths, immediately returning a `204 No Content` status containing wildcard CORS headers.

### Custom Headers Injected on all Responses:
* `Access-Control-Allow-Origin`: `*` (Wildcard allowing local browser port 8080 to communicate with API port 3000)
* `Access-Control-Allow-Methods`: `GET, POST, OPTIONS`
* `Access-Control-Allow-Headers`: `Content-Type, Authorization, TRACKER_KEY`

### Rationale
- **Cross-Origin Sandbox Safety**: Standard web browsers forbid pages loaded from `localhost:8080` from making HTTP `fetch()` requests to `localhost:3000` unless the server explicitly grants cross-origin rights via preflight headers. Emulating this preflight flow avoids browser sandboxing blocks.

---

## 3. Local JSON Database Synchronization

### Decision
Store telemetry and banking caches in `web/web_local_db.json`.
- **On Boot**: The Python server reads `web_local_db.json`. If missing, it instantiates an empty, pre-structured JSON schema database.
- **On mutative Writes (`POST`)**: The handler parses JSON bodies, applies atomic additions, writes the updated dictionary back to `web_local_db.json` via standard file-writes (`json.dump`), and returns `201 Created`.
- **On Reads (`GET`)**: The handler reads the file directly and serves the appropriate key mappings.

### Rationale
- **Fidelity Mapping (Principle IV)**: Preserves telemetry state across workstation boots and allows developers to inspect, modify, or corrupt the local database file (`web_local_db.json`) manually using any text editor, providing an exceptionally robust debugging cycle.
