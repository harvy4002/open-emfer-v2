# Feature Specification: Grafana-Style Public Dashboard and Participant Admin

**Feature Branch**: `002-public-dashboard`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "I also want to create the public dashboard in this app as well. So there is a backend admin/dashboard area for participants to collect the data and then there is a public dashbaord showing all of the data in various formats. The public one will be styled more like graphana."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Public Telemetry Dashboard (Priority: P1)

As a camp visitor or attendee, I want to access a public web-based dashboard styled with grid-based visual widgets (similar to Grafana) to view aggregate statistics, ambient environmental data, transactions, and current tracking status in real time.

**Why this priority**: Core feature requested. It provides public visibility of the camp data, allowing attendees and fans of the tracking project to see active updates.

**Independent Test**: Can be tested by opening the public dashboard root URL in a browser and verifying that all charts, numeric counters, and status indicators load data from the public endpoints (like GET `/beer`, GET `/browan`, etc.) without requiring authentication headers.

**Acceptance Scenarios**:

1. **Given** the public dashboard is loaded, **When** the user views the landing page, **Then** they see panels for: total drinks consumed, current status (e.g., "chilling"), latest temperature/ambient noise level, and recent campsite expenditures.
2. **Given** the public dashboard has loaded, **When** new telemetry is received in the backend, **Then** the public dashboard panels update either periodically or dynamically to reflect the latest values without requiring a full browser refresh.

---

### User Story 2 - View Backend Participant Admin Dashboard (Priority: P1)

As a tracking participant or admin, I want to access an authenticated backend admin dashboard to manually log activities (drinks, learning sessions, status) and manage the telemetry stream.

**Why this priority**: This is the admin interface for data collection. Without it, manual telemetry data (like drinks consumed or lecture status) can only be sent using manual API client calls.

**Independent Test**: Navigating to `/admin`, entering the `tracker_key` authorization, submitting a new drink payload, and verifying that the backend records the drink and the dashboard counts increment.

**Acceptance Scenarios**:

1. **Given** a tracking participant is on the `/admin` area, **When** they submit a new "Beer" or "Status Update" via the admin forms with a valid `tracker_key`, **Then** the request is sent with the appropriate authorization header and the update is saved.
2. **Given** an unauthorized visitor tries to access `/admin` actions, **When** they attempt to submit a status update, **Then** they are prompted for or denied via a `401 Unauthorized` API response.

---

### User Story 3 - Custom Layout and Panel Toggles (Priority: P3)

As a dashboard viewer, I want to toggle between different visualization formats (graphs, progress bars, numeric counters, status badges) for various telemetry metrics so that I can consume the data in different visual styles.

**Why this priority**: Enhances the visual user experience by providing standard interactive visual controls, similar to Grafana's multi-panel capabilities.

**Independent Test**: Clicking formatting/layout options on the dashboard switches panel display types without losing state or needing a database fetch.

**Acceptance Scenarios**:

1. **Given** the public dashboard has loaded, **When** the user clicks on a panel's display settings, **Then** they can toggle between a line graph view and a bar chart view of the environmental temperature.

---

### Edge Cases

- **Offline / Stale State**: If the backend API becomes unreachable or returns an error, the dashboard panels must show a clear, user-friendly "Disconnected" or "Stale Data" warning indicator instead of crashing, and resume normal operations once the connection is restored.
- **Empty Datasets**: If a category has no telemetry data yet (e.g. start of camp), the panels should display `0` or "No data available" gracefully with a placeholder chart, rather than showing blank space or throwing JS errors.
- **Invalid Admin Key**: If the cached `tracker_key` in the admin area expires or is invalid, all mutative forms should disable submissions and show a prominent authentication error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Public Display)**: The public dashboard MUST display real-time tracking data including: total drinks, current status (with active image URL), environmental temperature, ambient noise level, and camp expenditure.
- **FR-002 (Admin Logging Form)**: The admin dashboard MUST provide forms to manually log camper telemetry: posting drinks, changing current status, tracking lecture learning starts/stops, and initiating a tracker reset.
- **FR-003 (Grafana Aesthetic)**: The public dashboard UI MUST employ a dark-theme, grid-based layout inspired by Grafana, using visual counters, trend lines, and gauge panels for key metrics.
- **FR-004 (Auto-Refresh)**: The public dashboard MUST automatically refresh its panels at regular, configurable intervals (e.g. every 60 seconds) without requiring a full browser reload.
- **FR-005 (Admin Authorization)**: The admin dashboard MUST prompt the participant for the `tracker_key` and include it as an authorization header on all mutative requests to the backend API.
- **FR-006 (Responsive Design)**: The dashboard MUST be fully responsive, leveraging Bulma CSS or pure CSS to adjust panel sizing dynamically from mobile devices to large telemetry displays.
- **FR-007 (Dashboard Layout)**: The public dashboard MUST utilize a fixed, pre-configured layout optimized for both mobile and desktop screens, structured for future extension into multiple visual presets if additional telemetry fields are added.

### Key Entities *(include if feature involves data)*

- **DashboardPanel**: Represents a single visual card on the public dashboard. Key attributes: metric type, chart style (gauge/counter/line), refresh frequency, layout grid coordinates.
- **AdminSession**: Represents the current participant session in the admin area, caching the `tracker_key` locally.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The public dashboard loads fully and displays all panels in under 2 seconds on a standard mobile connection.
- **SC-002**: 100% of telemetry panels display correctly with a dark-mode theme and clear visual indicators (no raw JSON exposed on the public dashboard).
- **SC-003**: Public viewers can access and view all telemetry panels on the public dashboard without being prompted for credentials or keys.
- **SC-004**: 100% of manual telemetry logs submitted through the admin dashboard are rejected with a 401 Unauthorized unless the correct `tracker_key` is supplied.

## Assumptions

- **Assumption 1**: The public dashboard is a pure static web app (HTML/CSS/JS) that runs entirely in the browser and calls the existing AWS API Gateway endpoints.
- **Assumption 2**: Sourcing Grafana-like charting will be accomplished using a lightweight browser-native charting library (e.g., Chart.js or similar via CDN) without introducing complex NPM build pipelines.
- **Assumption 3**: The `tracker_key` will be stored in the admin user's browser local storage to preserve authentication state across browser sessions.
