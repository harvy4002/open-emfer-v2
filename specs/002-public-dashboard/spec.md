# Feature Specification: Grafana-Style Public Dashboard

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

### User Story 2 - Custom Layout and Panel Toggles (Priority: P3)

As a dashboard viewer, I want to toggle between different visualization formats (graphs, progress bars, numeric counters, status badges) for various telemetry metrics so that I can consume the data in different visual styles.

**Why this priority**: Enhances the visual user experience by providing standard interactive visual controls, similar to Grafana's multi-panel capabilities.

**Independent Test**: Clicking formatting/layout options on the dashboard switches panel display types without losing state or needing a database fetch.

**Acceptance Scenarios**:

1. **Given** the public dashboard has loaded, **When** the user clicks on a panel's display settings, **Then** they can toggle between a line graph view and a bar chart view of the environmental temperature.

---

### Edge Cases

- **Offline / Stale State**: If the backend API becomes unreachable or returns an error, the dashboard panels must show a clear, user-friendly "Disconnected" or "Stale Data" warning indicator instead of crashing, and resume normal operations once the connection is restored.
- **Empty Datasets**: If a category has no telemetry data yet (e.g. start of camp), the panels should display `0` or "No data available" gracefully with a placeholder chart, rather than showing blank space or throwing JS errors.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (Public Display)**: The public dashboard MUST display real-time tracking data including: total drinks, current status (with active image URL), environmental temperature, ambient noise level, and camp expenditure.
- **FR-002 (Grafana Aesthetic)**: The public dashboard UI MUST employ a dark-theme, grid-based layout inspired by Grafana, using visual counters, trend lines, and gauge panels for key metrics.
- **FR-003 (Auto-Refresh)**: The public dashboard MUST automatically refresh its panels at regular, configurable intervals (e.g. every 60 seconds) without requiring a full browser reload.
- **FR-004 (Responsive Design)**: The dashboard MUST be fully responsive, leveraging Bulma CSS or pure CSS to adjust panel sizing dynamically from mobile devices to large telemetry displays.
- **FR-005 (Dashboard Layout)**: The public dashboard MUST utilize a fixed, pre-configured layout optimized for both mobile and desktop screens, structured for future extension into multiple visual presets if additional telemetry fields are added.

### Key Entities *(include if feature involves data)*

- **DashboardPanel**: Represents a single visual card on the public dashboard. Key attributes: metric type, chart style (gauge/counter/line), refresh frequency, layout grid coordinates.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The public dashboard loads fully and displays all panels in under 2 seconds on a standard mobile connection.
- **SC-002**: 100% of telemetry panels display correctly with a dark-mode theme and clear visual indicators (no raw JSON exposed on the public dashboard).
- **SC-003**: Public viewers can access and view all telemetry panels on the public dashboard without being prompted for credentials or keys.

## Assumptions

- **Assumption 1**: The public dashboard is a pure static web app (HTML/CSS/JS) that runs entirely in the browser and calls the existing AWS API Gateway endpoints.
- **Assumption 2**: Sourcing Grafana-like charting will be accomplished using a lightweight browser-native charting library (e.g., Chart.js or similar via CDN) without introducing complex NPM build pipelines.
