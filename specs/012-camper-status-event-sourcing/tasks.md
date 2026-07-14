# Tasks: Event-Sourced Camper Status Image Matching

**Input**: Design documents from `/specs/012-camper-status-event-sourcing/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Unit tests are not requested in the specification; validation will be conducted interactively using the local Python socket simulator and the Quickstart Validation scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verifying local development workspace and backend files

- [X] T001 Verify that `backend/sim_server.py` and `web/js/app.js` are fully prepared for status event-sourcing refactoring

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Preparing case-insensitive security headers on the server

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Implement case-insensitive authorization header checks (extracting Authorization, authorization, tracker_key, and TRACKER_KEY) inside `lambda_handler` inside `backend/sim_server.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Explicit Status Image Mapping (Priority: P1) 🎯 MVP

**Goal**: Store active status using event sourcing and map custom texts to available photo assets

**Independent Test**: Navigate to Charlotte's dashboard (`u=cha`). Log "Coding" under Camper Status, and verify Charlotte's profile image updates to `/cha_status/cha_workshop.jpg` successfully.

### Implementation for User Story 1

- [X] T003 [US1] Refactor the GET `/beer` status endpoint inside `backend/sim_server.py` to retrieve all chronological events and strictly filter for explicit `Status` / `status` event types
- [X] T004 [P] [US1] Bind the local `activeUser` variable directly to the global `window.activeUser` object inside `web/js/app.js` across load, popstate, and navigation switch handlers
- [X] T005 [P] [US1] Implement `resolveStatusImage(statusText)` inside `web/js/app.js` to fuzzy-match custom string inputs to the exact 11 local picture filenames
- [X] T006 [P] [US1] Update `fetchTelemetry` inside `web/js/app.js` to call `resolveStatusImage` and dynamically load the resolved asset path

**Checkpoint**: At this point, explicit event-sourced status photo mapping is fully functional across campers.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Walker validations and verification run

- [X] T007 Run local simulator and execute the entire `specs/012-camper-status-event-sourcing/quickstart.md` validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3)**: All depend on Foundational phase completion.
- **Polish (Final Phase)**: Depends on all user stories being complete.

### Parallel Opportunities

- Frontend changes (T004, T005, T006) can run in parallel with backend filtering updates (T003).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Server filtering + JS fuzzy matcher)
4. Run Polish & walkthrough validation checks
