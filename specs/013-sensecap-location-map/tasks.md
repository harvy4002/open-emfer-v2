# Tasks: Sensecap Location Map Integration

**Input**: Design documents from `specs/013-sensecap-location-map/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Explicit file paths are included in descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and loading external Leaflet assets.

- [X] T001 Import Leaflet CSS and JS library from unpkg CDN (`https://unpkg.com/leaflet@1.9.4/dist/leaflet.css` and `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js`) into the `<head>` of `web/index.html`.
- [X] T002 Add a Leaflet stylesheet override block inside `web/index.html` to style map tooltips and set basic Leaflet container constraints.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and state management setup.

- [X] T003 Ensure that any local state schema retrieved from the GET `/history` endpoint contains a valid sequence of `lat`, `lng`, and ISO `time` string elements inside `backend/sim_server.py`.
- [X] T004 Run and verify backend simulation tests using `pytest` inside the terminal to confirm the `/history` endpoint works as expected.

---

## Phase 3: User Story 1 - Interactive Map Visualization on Public Dashboard (Priority: P1) 🎯 MVP

**Goal**: Integrate Leaflet.js with EMF tiles and plot markers and polyline for fetched coordinate checks on the dashboard.

**Independent Test**: Load the public dashboard at `web/index.html?u=hvy`. Check that the `#map-overlay-view` panel is visible, initializes an interactive map centered at `52.0411, -2.3784`, fetches actual coordinates from `/history`, and plots a polyline connecting them.

### Implementation for User Story 1

- [X] T005 [US1] Remove the static canvas `<canvas id="map-trail-canvas">` and card background image styling inside `web/index.html` under the `Camper Location History Map` section, replacing it with a clean container `<div id="map-container" style="width: 100%; height: 300px; border-radius: 4px; border: 1px solid #2c2f33;"></div>`.
- [X] T006 [US1] Create a global `mapInstance` variable and write `initializeMap()` function inside `web/js/app.js` to instantiate `L.map('map-container')` with default center `[52.0411, -2.3784]` and zoom level 16.
- [X] T007 [US1] Implement primary tile layer rendering using `L.tileLayer('https://map.emfcamp.org/tiles/{z}/{x}/{y}.png')` with attribution inside `web/js/app.js`.
- [X] T008 [US1] Add a load failure event handler on the custom EMF tile layer to automatically fall back to loading the standard OpenStreetMap tile layer (`https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`) inside `web/js/app.js`.
- [X] T009 [US1] Refactor `drawLocationTrail` inside `web/js/app.js` to accept `locationHistory` coordinates array, clear previous markers/polylines, and draw the coordinate checks as Leaflet marker pins connected by an `L.polyline`.

**Checkpoint**: User Story 1 is fully functional and testable independently. Loading the dashboard renders a real interactive map with a trail representation.

---

## Phase 4: User Story 2 - Plotting 3-Hour Historical Location Trail (Priority: P2)

**Goal**: Filter coordinates array to points within 3 hours of the latest point and add interactive tooltips showing timestamp and cumulative telemetry.

**Independent Test**: Supply mock coordinates spanning 6 hours to `/history`. Open `web/index.html?u=hvy` and verify that only coordinates recorded within 3 hours of the last coordinate are mapped. Verify clicking markers displays a popup with coordinates, steps, and distance.

### Implementation for User Story 2

- [X] T010 [US2] Implement client-side timestamp delta filtering logic in `drawLocationTrail` inside `web/js/app.js` to determine the latest coordinate timestamp, filter the `locationHistory` array, and keep only points recorded $\le$ 3 hours relative to that timestamp.
- [X] T011 [US2] Implement distinguished marker styling inside `web/js/app.js`: render the most recent/latest coordinate with a prominent custom Leaflet marker or larger red pulsing `L.circleMarker`, and preceding coordinates as smaller orange trailing dots.
- [X] T012 [US2] Implement interactive popup bindings on each plotted marker using Leaflet's `.bindPopup(...)` inside `web/js/app.js`, displaying the timestamp (formatted locally as HH:MM:SS), cumulative distance (km), and cumulative steps.

**Checkpoint**: User Story 2 is complete. Coordinates are filtered to a 3-hour sliding window relative to the latest signal, with full interactive popups.

---

## Phase 5: User Story 3 - Ingesting Location Payloads & Generating Mock Simulation Data (Priority: P3)

**Goal**: Add simulator options and endpoints to generate a winding campsite trail winding through Eastnor Castle spanning 3 hours.

**Independent Test**: Open the simulator panel `web/simulator.html` under the "Sensecap GPS Ingest" card, click the newly added "Generate Mock 3-Hour Trail" button, then visit the public dashboard to observe exactly 3 hours of coordinate points plotted.

### Implementation for User Story 3

- [X] T013 [P] [US3] Add a preset array of 4 sequential coordinate points winding around Eastnor Castle (`52.0411, -2.3784`) spanning a 4-hour chronological range inside `web/js/simulator.js`.
- [X] T014 [US3] Add a button labeled `<button class="button is-warning" id="btn-inject-3h-trail">Generate Mock 3-Hour Trail</button>` to the Sensecap panel inside `web/simulator.html`.
- [X] T015 [US3] Implement client-side click event listener for `#btn-inject-3h-trail` inside `web/js/simulator.js` to sequentially POST the 4 coordinates to `/sensecap` with staggered timestamps relative to the current real time (e.g., `-180 mins`, `-120 mins`, `-60 mins`, `now`).

**Checkpoint**: All user stories are independently functional. Simulation and testing loop is fully closed.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimizations and responsiveness checks.

- [X] T016 [P] Ensure Leaflet canvas containers resize properly and display responsively on mobile device layouts inside `web/index.html`.
- [X] T017 [P] Execute quickstart.md validation instructions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User stories then proceed in sequence (P1 → P2 → P3).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

```text
+---------------+
| Phase 1 Setup |
+---------------+
        |
        v
+----------------------+
| Phase 2 Foundational |
+----------------------+
        |
        +-----------------------------------------+
        |                                         |
        v                                         v
+--------------------------+          +--------------------------+
| Phase 3 User Story 1 (P1)|          | Phase 5 User Story 3 (P3)|
+--------------------------+          +--------------------------+
        |
        v
+--------------------------+
| Phase 4 User Story 2 (P2)|
+--------------------------+
        |
        v
+--------------------------+
|   Phase 6 Polish & E2E   |
+--------------------------+
```

### Parallel Opportunities

- Importing assets (**T001**) and creating CSS overrides (**T002**) can run in parallel.
- Setting up coordinate lists in the simulator client (**T013**) can run in parallel with the main map implementation.

---

## Parallel Example: Setup & Story 3 Prep

```bash
# Developer A: Setup primary Leaflet inclusions
Task: "Import Leaflet CSS and JS library from unpkg CDN in web/index.html"

# Developer B: Prepare simulator mock coordinates array
Task: "Add a preset array of 4 sequential coordinate points winding around Eastnor Castle inside web/js/simulator.js"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: Verify that the interactive Leaflet map renders correctly.

### Incremental Delivery

1. Setup CDN inclusion & container → Page loads without errors.
2. Add map initialization & EMF tile layers → Empty map centers correctly.
3. Hook up history coordinate trail plotting → Trail renders (MVP achieved!).
4. Apply 3-hour timestamp filtering → Older coords filtered.
5. Add tooltips/popups → Complete interactive user experience.
6. Add simulator mock trigger button → Seamless, ultra-fast developer verification.
