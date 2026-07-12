# Feature Specification: Local Developer Simulator

**Feature Branch**: `005-local-dev-simulator`

**Created**: 2026-07-10

**Status**: Ready

**Input**: User description: "this needs to be developed as fast as possible so needs userfeedback in the tighest loop. Make it so the app can be spun up locally, representing the final websites both backend and public dashboards. I want the ability to trigger APIs in a web interface as well, so I can quickly test all the features of the app."

---

## Purpose and Overview

The **Local Developer Simulator** provides a high-fidelity, offline sandbox environment for the entire Open EMF Camper ecosystem. It fulfills **Principle VIII (Fast Feedback Cycles)** of the Constitution by enabling developers and automated agents to:
1. Spin up both the public dashboard and the admin logging console locally on a lightweight static file server.
2. Interact with a web-based **API Playground (`simulator.html`)** containing mock data generators to manually inject sensor and bank telemetry flows.
3. Emulate all backend API routes (`/beer`, `/sensecap`, `/browan`, `/monzo`, `/history`) via a lightweight local Python server that simulates live AWS Lambda and DynamoDB response formats.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Local Web Server (Priority: P1)

As a developer, I want to run a single, zero-dependency local server command to run both the public dashboard and admin consoles, so that I can interact with the client-side screens without deploying to AWS S3.

**Why this priority**: Immediate feedback loop. Frontend developers need to preview layout, vertical stacked mobile elements, and Chart.js animations offline.

**Independent Test**: Execute the local serving script, open `http://localhost:8080/index.html` in a web browser, and verify that the page loads the static elements and Bulma grid assets correctly.

**Acceptance Scenarios**:

1. **Given** local web assets exist in `web/`, **When** the local serving command is run, **Then** the local server serves all static resources on port 8080 with appropriate mime types.

---

### User Story 2 - Interactive Web Playground (Priority: P1)

As a developer or tester, I want to access an interactive web playground (`simulator.html`) containing trigger forms and mock data presets, so that I can manually inject telemetry flows (e.g. mock T1000 GPS coordinate paths, Browan decibel spikes, Monzo transactions) and observe live data changes in real-time.

**Why this priority**: Tightest possible manual verification loop. Avoids having to write custom cURL statements or use external Postman scripts.

**Independent Test**: Load `http://localhost:8080/simulator.html`, select the "T1000 Sensor" card, click "Generate Random Path", tap "Inject Payload", and confirm that the dashboard instantly increments the camper's step counter and maps the new coordinates.

**Acceptance Scenarios**:

1. **Given** the simulator web page is open, **When** a user clicks "Trigger Monzo Sync Simulation", **Then** the page sends an HTTP POST simulating the Monzo background cron job and renders a success log banner.
2. **Given** any payload injection form is submitted, **When** the request is made, **Then** the playground displays the exact raw HTTP payload, headers, and simulated response payload for debugging.

---

### User Story 3 - Local API Simulator (Priority: P2)

As an engineer, I want to run a lightweight, local mock API backend in Python, so that the static frontend pages can execute authentic `fetch` requests and persist mock telemetry state without needing live AWS credentials.

**Why this priority**: Eliminates cloud deployment blockers, allowing full end-to-end client-to-backend integration testing offline.

**Independent Test**: Start the local Python API simulator on port 3000, send an authorized POST to `/beer` from the local web browser, and verify that the console prints a transaction log trace and returns `201 Created` with correct JSON.

**Acceptance Scenarios**:

1. **Given** the local Python API server is running, **When** any public telemetry GET endpoint is queried, **Then** it serves the corresponding pre-aggregated statistics or latest state cached in a local JSON file database (`web_local_db.json`), ensuring mock telemetry state persists across server restarts for high-fidelity offline testing.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Lightweight Local Server)**: The workspace MUST provide a single-command utility (e.g. python-native static file server) to run the static S3 frontend pages on `http://localhost:8080`.
- **FR-002 (Web-Based Playground)**: The project MUST include an interactive web page `web/simulator.html` containing pre-configured logging, IoT, and banking payload templates to manually trigger telemetry events.
- **FR-003 (Payload Inspector)**: The API playground MUST display a live request/response console log detailing the exact JSON payload, HTTP method, and response status of all simulated triggers.
- **FR-004 (Local API Emulator)**: The system MUST provide a lightweight Python API simulator script `backend/sim_server.py` that listens on port 3000, intercepts CORS preflights, and emulates all API Gateway routes.
- **FR-005 (CORS Off)**: The local API server MUST support automatic CORS wildcard response headers (`Access-Control-Allow-Origin: *`) to ensure local browsers on port 8080 can communicate with port 3000 without sandbox blocks.
- **FR-006 (Configurable Host URL)**: Client-side JS scripts (`app.js`, `admin.js`) MUST dynamically select the API base host URL: pointing to `http://localhost:3000` when running locally, and pointing to the production CloudFront API gateway URL when deployed in the cloud.

### Key Entities

- **MockUplink**: Represents the simulated JSON request payload generated by the API playground forms.
- **LocalTelemetryState**: In-memory or transient storage keeping track of aggregate counters and coordinates.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the local server scripts exposes both public and admin dashboards in under 1 second.
- **SC-002**: 100% of telemetry payloads triggered in the web playground (`simulator.html`) are processed by the local API server and saved within 100ms.
- **SC-003**: The client scripts automatically route all API requests to the local port 3000 when the window hostname is `localhost` or `127.0.0.1`.

## Assumptions

- **Assumption 1**: Python 3 is installed and globally available on the developer's local system.
- **Assumption 2**: Chart.js and Bulma CSS assets can be loaded over public CDNs during local developer previews.
