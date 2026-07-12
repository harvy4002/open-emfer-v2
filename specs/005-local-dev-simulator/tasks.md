# Tasks: Local Developer Simulator

**Input**: Design documents from `specs/005-local-dev-simulator/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Scenario testing is handled natively via the web playground UI as defined in `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Codebase structured as a decoupled Python/S3 static file server.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize the Python-based API server file skeleton in `backend/sim_server.py`
- [x] T002 Initialize the local developer playground HTML file skeleton in `web/simulator.html`
- [x] T003 [P] Create the default JSON database schema file in `web/web_local_db.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement local JSON database reading, bootstrapping, and automatic file creation logic inside `backend/sim_server.py`
- [x] T005 [P] Implement options preflight interception and wildcard CORS headers injection in `backend/sim_server.py`
- [x] T006 [P] Add CDN stylesheet and script imports for Bulma CSS and Chart.js inside `web/simulator.html`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Local Web Server (Priority: P1) 🎯 MVP

**Goal**: Zero-dependency static file server to host and preview the public and admin dashboards locally.

**Independent Test**: Spin up the static file server, load `http://localhost:8080/index.html` in a web browser, and verify pages render correctly.

### Implementation for User Story 1

- [x] T007 [US1] Implement dynamic API host selection (using `localhost:3000` when running locally, and production gate URLs when in the cloud) inside `web/js/app.js` and `web/js/admin.js`
- [x] T008 [P] [US1] Write Python-native static file serving commands in `specs/005-local-dev-simulator/quickstart.md`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Interactive Web Playground (Priority: P1)

**Goal**: Web-based developer playground with forms to manually trigger telemetry payloads and inspect request logs.

**Independent Test**: Load `simulator.html` in browser, submit a mock coordinate, and check that the logging console panels output a successful POST event.

### Implementation for User Story 2

- [x] T009 [US2] Implement mock coordinates generator and forms binding for T1000 GPS payloads in `web/simulator.html`
- [x] T010 [P] [US2] Implement form controllers for Browan sound decibels and Monzo bank transactions in `web/simulator.html`
- [x] T011 [US2] Implement JavaScript event controllers inside `web/js/simulator.js` to capture playground submits and POST JSON to API port 3000
- [x] T012 [US2] Implement the live request/response Console Log inspector panel in `web/simulator.html` and `web/js/simulator.js`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Local API Simulator (Priority: P2)

**Goal**: Python API server emulating Lambda endpoints, pre-aggregating statistics, and writing to `web_local_db.json`.

**Independent Test**: Run the API server, trigger a drink log from playground, and verify `web_local_db.json` updates and terminal prints transaction logs.

### Implementation for User Story 3

- [x] T013 [US3] Implement POST `/beer` route parser to increment individual and combined aggregates and write raw logs to `backend/sim_server.py`
- [x] T014 [US3] Implement POST `/sensecap` and `/browan` route parsers, Haversine step-proxy solvers, and 20-entry history array bounds in `backend/sim_server.py`
- [x] T015 [US3] Implement POST `/monzo` background synchronization mock route in `backend/sim_server.py`
- [x] T016 [US3] Implement GET `/beer`, GET `/history`, and GET `/monzo` read routes fetching from `web/web_local_db.json` inside `backend/sim_server.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Code formatting and final validation

- [x] T017 Run python formatting and style checks in `backend/sim_server.py` using ruff
- [x] T018 Verify mobile responsiveness and vertical column stackings of `web/simulator.html` down to 320px
- [x] T019 [P] Execute full end-to-end data flow validation scenarios defined in `specs/005-local-dev-simulator/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 parameters
- **User Story 3 (P3)**: Depends on Phase 2 base infrastructure, can run independently

---

## Parallel Example: User Story 1

```bash
# Initialize file skeletons simultaneously:
# T002 [P] and T003 [P] can run concurrently
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently
4. Add User Story 3 → Test independently
