# Feature Specification: Sensecap Location Map Integration

**Feature Branch**: `013-sensecap-location-map`

**Created**: 2026-07-14

**Status**: Draft

**Input**: User description: "Capture location information from sensecap and plot a path of the last 3 hours on the map. Use some fake data for testing. The map is provided here: https://map.emfcamp.org/#16/52.0411/-2.3784 so find the underlying data for it and import it to the public dashboard. The location for this event will be in this map."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive Map Visualization on Public Dashboard (Priority: P1)

As an attendee visiting the public camper dashboard, I want to see an interactive map centered around the EMF Camp site (Eastnor Castle) with the active camper's current position and coordinate breadcrumbs so that I can immediately know where they are.

**Why this priority**: Core value of tracking and map visualization. It replaces the static/fake background image with a real, interactive map that loads EMF Camp specific cartography.

**Independent Test**: The dashboard can be loaded with any camper profile selected (e.g. Harvy), rendering an interactive Leaflet map that loads map.emfcamp.org tiles and highlights their last reported location.

**Acceptance Scenarios**:

1. **Given** the public dashboard is loaded with a participant's profile, **When** the location history is rendered, **Then** an interactive Leaflet map centered at `52.0411, -2.3784` with zoom level 16 is displayed, using the `map.emfcamp.org` tile layer.
2. **Given** the participant has location history, **When** the map is rendered, **Then** a marker is placed at the most recent coordinate and a path is plotted connecting the historical coordinates.

---

### User Story 2 - Plotting 3-Hour Historical Location Trail (Priority: P2)

As a viewer of the telemetry tracker, I want to see the specific trail/path showing where the camper has walked over the last 3 hours, so that I can visualize their route history across the camp.

**Why this priority**: Crucial for tracking trends and paths without cluttering the map with outdated or irrelevant historic positions. It bounds the map path strictly to the last 3 hours of telemetry data.

**Independent Test**: By sending Sensecap location payloads spanning multiple hours, verify that only coordinates within the last 3 hours are plotted on the map, with clear timestamp labels on markers.

**Acceptance Scenarios**:

1. **Given** a camper's location history spanning 6 hours, **When** the dashboard loads, **Then** only the location points recorded within the last 3 hours of the latest point are displayed on the map, and older points are filtered out of the mapped path.
2. **Given** a location coordinate marker on the map, **When** a user clicks on a breadcrumb marker, **Then** a popup is shown displaying the timestamp (formatted as local HH:MM:SS) and cumulative distance/steps at that point.

---

### User Story 3 - Ingesting Location Payloads & Generating Mock Simulation Data (Priority: P3)

As a developer/tester, I want to be able to send real-time coordinates to the `/sensecap` endpoint, and have a rich set of mock simulation data automatically generated that spans the last 3 hours, so that I can verify the map rendering and path filtering without needing a physical T1000 device.

**Why this priority**: Necessary for validation and development feedback loop (Principle VIII of the Constitution).

**Independent Test**: Verify that running a test script or simulator action posts multiple coordinate points to `/sensecap` spread across the last 3 hours, which instantly populates `/history` and updates the interactive map correctly.

**Acceptance Scenarios**:

1. **Given** a simulator POST payload request to `/sensecap` with sequential coordinates spanning the last 3 hours, **When** the backend processes these payloads, **Then** the location history is successfully updated in DynamoDB state, maintaining correct order.
2. **Given** a developer wants to test the 3-hour map plotting, **When** they run the local dev simulator or visit the local simulator view, **Then** they can trigger a "Generate Mock 3-Hour Trail" preset that injects coordinates winding through Eastnor Castle's campsite coordinates.

### Edge Cases

- **No Location Data**: What happens when the camper has no location data recorded? The map should render with a placeholder or default center at the EMF Camp coordinates `52.0411, -2.3784`, showing a friendly message that no GPS signal has been acquired yet.
- **Tile Server Offline**: What happens if the `map.emfcamp.org` tile server is offline or unreachable? The dashboard map must seamlessly fallback to standard OpenStreetMap tiles (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`) so that the map layout does not break.
- **Outside Bounds**: What happens if coordinates are outside of the EMF Camp bounding box? The map should adjust its bounds to fit the points, but default view remains centered on EMF Camp.
- **Single Coordinate Point**: What happens if there's only a single location point in the last 3 hours? The map should show a single marker representing the current position without a path line, preventing rendering errors.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST replace the static image card on the public dashboard with an interactive Leaflet-based map widget.
- **FR-002**: The interactive map MUST default to a center coordinate of `52.0411` latitude and `-2.3784` longitude (the EMF Camp 2026 site at Eastnor Castle) at zoom level 16.
- **FR-003**: The map MUST use `https://map.emfcamp.org/tiles/{z}/{x}/{y}.png` as its primary tile layer, with automatic fallback to standard OpenStreetMap tiles (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`) on error or load failure.
- **FR-004**: The system MUST filter the coordinates retrieved from the `/history` endpoint, plotting only points where the timestamp is within 3 hours (relative to the latest coordinate's timestamp) of the latest coordinate point's timestamp.
- **FR-005**: The plotted path MUST feature a distinguished marker (e.g., custom color, pulsing, or larger size) for the most recent coordinate, and smaller connected breadcrumbs for previous coordinates.
- **FR-006**: Each breadcrumb/marker on the map MUST display an interactive popup or tooltip with the timestamp and, if available, the cumulative distance (km) and cumulative steps.
- **FR-007**: The local simulator (`sim_server.py` and `simulator.html`) MUST provide a manual data injection option to generate and send a 3-hour mock route of coordinates within the EMF Camp bounding box to `/sensecap`.
- **FR-008**: The map MUST display the selected active camper's trail only, but the underlying data structures and mapping logic MUST be designed extensibly to support displaying multiple concurrent camper trails in the future.

### Key Entities *(include if feature involves data)*

- **LocationHistoryState**: Part of the DynamoDB state containing `cumulative_distance_km`, `cumulative_steps`, and `location_history` (list of `LocationPoint` objects).
- **LocationPoint**: An individual coordinates record containing `lat`, `lng`, and `time` (ISO timestamp).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The interactive map loads and renders in under 1.5 seconds on the public dashboard.
- **SC-002**: 100% of location markers plotted are within the last 3 hours of the most recent telemetry update, with any older points excluded from the visualized trail.
- **SC-003**: The map successfully falls back to OpenStreetMap within 2 seconds if the custom EMF tile server is unavailable or fails to load.
- **SC-004**: Users can click or hover on any path node to instantly view its exact timestamp and distance telemetry.

## Assumptions

- **Assumption 1**: The user's browser has internet connectivity to load Leaflet from unpkg.com and tile images from `map.emfcamp.org` or `openstreetmap.org`.
- **Assumption 2**: Location points stored in DynamoDB/simulator state contain valid ISO 8601 timestamps and decimal coordinates within or near the EMF Camp bounding area (`52.03` to `52.05` latitude, `-2.39` to `-2.36` longitude).
- **Assumption 3**: The EMF Camp tile server `https://map.emfcamp.org/tiles/{z}/{x}/{y}.png` is configured to support standard tile request formats and cross-origin (CORS) resource sharing if accessed directly, or we can use standard Leaflet tile loading mechanisms.
- **Assumption 4**: Only participants with a tracker (e.g. Harvy) will have the map overlay panel rendered, keeping other participant views uncluttered.
