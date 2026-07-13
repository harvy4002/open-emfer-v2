# Tasks: Public Landing Page and Dynamic Dashboard Routing

**Input**: Design documents from `/specs/008-public-landing-page/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- HTML document: `web/index.html`
- JavaScript controller: `web/js/app.js`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Basic verification of development server environment.

- [X] T001 Verify local web serving configuration for `web/` directory using `python3 -m http.server -d web 8080`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core UI visibility elements and division of layout containers.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Define the helper CSS rule `.hidden { display: none !important; }` in the stylesheet within `web/index.html`
- [X] T003 Isolate existing Grafana-style telemetry panels inside a single parent container `#dashboard-view` in `web/index.html`
- [X] T004 Create the empty `#intro-landing-view` container element as a placeholder for landing content in `web/index.html`

**Checkpoint**: Core view containers established. User story implementation can now begin.

---

## Phase 3: User Story 1 - Welcoming Project Introduction (Priority: P1) 🎯 MVP

**Goal**: Welcoming landing page introducing the Open EMF Camper project when accessing the root URL with no parameter.

**Independent Test**: Navigate to root `index.html` without parameters. Verify introduction text is shown and dashboard panels are hidden.

- [X] T005 [P] [US1] Create the static introduction card HTML content inside `#intro-landing-view` in `web/index.html`, explaining EMF camp, LoRa telemetry, step tracking, and Monzo expenses sync.
- [X] T006 [P] [US1] Implement load-time URL query parameter parsing for `u` (or `user_id`) inside `web/js/app.js`.
- [X] T007 [US1] Implement core view routing toggle logic in `web/js/app.js` to hide `#dashboard-view` and show `#intro-landing-view` if no parameters are present.

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Seamless Telemetry Dashboard Bypass (Priority: P1)

**Goal**: Instant rendering of individual camper dashboards when loaded with URL query parameters.

**Independent Test**: Navigate to `index.html?u=cha`. Verify introduction card is hidden and Charlotte's dynamic widgets load.

- [X] T008 [P] [US2] Define a hardcoded participant registry map (`hvy`, `cha`, `ash`, `tin`, `combined` with names) in `web/js/app.js` to avoid external API calls (AWS Free Tier optimized).
- [X] T009 [US2] Update page-load initialization in `web/js/app.js` to ignore `localStorage` cached user state on initial direct load if no URL parameters are present, prioritizing the introductory landing page.
- [X] T010 [US2] Update URL routing logic in `web/js/app.js` to immediately show `#dashboard-view`, hide `#intro-landing-view`, and load telemetry if a valid camper ID parameter is present.
- [X] T011 [US2] Implement fallback behavior in `web/js/app.js` to fallback gracefully to showing `#intro-landing-view` if an invalid or unrecognized camper ID parameter (e.g. `?u=xyz`) is supplied.

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Interactive Camper Portal Directory (Priority: P2)

**Goal**: Tactile quick links for Harvy, Charlotte, Ash, and Tina dashboards that update state via `pushState` history and handle browser Back/Forward navigation (`popstate`).

**Independent Test**: Click "Charlotte" portal button, verify URL updates to `?u=cha` and dashboard transitions dynamically. Click back, verify it transitions back to landing page introduction.

- [X] T012 [P] [US3] Create dedicated, mobile-optimized navigation buttons for Harvy, Charlotte, Ash, Tina, and Combined dashboards within `#intro-landing-view` in `web/index.html`.
- [X] T013 [P] [US3] Implement dynamic page transition function `selectCamperDashboard` inside `web/js/app.js` utilizing `window.history.pushState` to transition views without full page reloads.
- [X] T014 [US3] Register click event handler listeners on all quick link portal buttons in `web/js/app.js` to call the routing transition helper function.
- [X] T015 [US3] Register browser `popstate` event listener on `window` in `web/js/app.js` to dynamically handle history back/forward navigation, toggling view visibility states based on history parameters.

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [X] T016 Verify all interactive buttons and link elements on the landing page maintain a minimum 48px width/height sizing envelope in `web/index.html` to satisfy mobile-responsiveness constraints.
- [X] T017 Validate layout responsiveness down to 320px with zero horizontal scrolls for both view states in `web/index.html`.
- [X] T018 Run the complete end-to-end routing and popstate validation scenarios in `specs/008-public-landing-page/quickstart.md` using the local python server.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User stories proceed in priority order (US1 → US2 → US3).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories.
- **User Story 2 (P1)**: Can start after US1 - relies on parameters checks established.
- **User Story 3 (P2)**: Can start after US2 - provides portal directory buttons to load dashboards.

---

## Parallel Execution Opportunities

- Phase 3 Setup: `T005` (HTML) and `T006` (JS parameter parsing) can be implemented in parallel.
- Phase 4 Setup: Hardcoding participant registry `T008` can be done in parallel with other JS routing changes.
- Phase 5 Setup: Navigation buttons UI `T012` and transition JS function `T013` can be written in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready.
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!).
3. Add User Story 2 → Test independently → Deploy/Demo.
4. Add User Story 3 → Test independently → Deploy/Demo.
