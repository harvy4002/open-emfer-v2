# Tasks: Public Landing Page and Dynamic Dashboard Routing

**Input**: Design documents from `/specs/008-public-landing-page/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

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

**Purpose**: Project initialization and basic structure verification.

- [X] T001 Create feature checklists directory and copy standard index files in `specs/008-public-landing-page/`
- [X] T002 [P] Verify existing web directory structure and serve configurations in `backend/sim_server.py`
- [X] T003 [P] Verify code style configurations for ES6 standard JavaScript inside `web/js/app.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Define the standard CSS layout helper classes (specifically `.hidden` for display none) inside `web/index.html`
- [X] T005 [P] Isolate the main telemetry dashboard elements into a single parent layout container `#dashboard-view` inside `web/index.html`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Welcoming Project Introduction (Priority: P1) 🎯 MVP

**Goal**: Welcoming landing page introducing the Open EMF Camper project when accessing the root URL with no parameter.

**Independent Test**: Navigate to root `index.html` without parameters. Verify introduction text is shown and dashboard panels are hidden.

- [X] T006 [US1] Create the static introduction container `#intro-landing-view` with descriptive paragraphs explaining the project goals in `web/index.html`
- [X] T007 [US1] Implement load-time query parameter checking to detect the presence of `u` or `user_id` inside `web/js/app.js`
- [X] T008 [US1] Implement visibility toggles to show `#intro-landing-view` and hide `#dashboard-view` if parameters are absent inside `web/js/app.js`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Seamless Telemetry Dashboard Bypass (Priority: P1)

**Goal**: Instant rendering of individual camper dashboards when loaded with URL query parameters.

**Independent Test**: Navigate to `index.html?u=ali`. Verify introduction card is hidden and Alice's dynamic widgets load.

- [X] T009 [US2] Implement parameter bypass logic to hide `#intro-landing-view` and display `#dashboard-view` if a valid identifier is present inside `web/js/app.js`
- [X] T010 [US2] Configure page-load initialization to ignore local storage caches for view toggling when loading the raw root URL inside `web/js/app.js`
- [X] T011 [US2] Implement fallback routing to redirect unrecognized user IDs back to the introductory landing page inside `web/js/app.js`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Interactive Camper Portal Directory (Priority: P2)

**Goal**: Tactile quick links for Harvy, Alice, Bob, and Combined dashboards that update state via `pushState` history.

**Independent Test**: Click "Alice Smith" portal button, verify URL updates to `?u=ali` and dashboard transitions dynamically.

- [X] T012 [US3] Add quick-link action buttons for each active camper and the combined view inside the landing page container in `web/index.html`
- [X] T013 [US3] Implement the custom transition function `selectCamperDashboard` utilizing `window.history.pushState` inside `web/js/app.js`
- [X] T014 [US3] Update portal link elements and form fields to maintain a minimum of 48px tactile height inside `web/index.html`
- [X] T015 [US3] Register click handler events on all quick link buttons to call the dynamic router transition function in `web/js/app.js`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [X] T016 [P] Document and clean up styling references and unused layout rules inside `web/index.html`
- [X] T017 [P] Clean up console statements and refactor routing helper logic inside `web/js/app.js`
- [X] T018 Execute and validate all onboarding routing scenarios defined in `specs/008-public-landing-page/quickstart.md` using the local python server

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

- Setup tasks `T002` and `T003` can run in parallel.
- Foundational task `T005` can run in parallel with `T004`.
- Polish tasks `T016` and `T017` can run in parallel once US3 is implemented.

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
