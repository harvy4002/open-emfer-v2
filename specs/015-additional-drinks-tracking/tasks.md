# Tasks: Additional Drinks Tracking and Dynamic Public Dashboard Breakdown

**Input**: Design documents from `/specs/015-additional-drinks-tracking/`

**Prerequisites**: plan.md (required), spec.md (required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project and workspace environment initialization

- [x] T001 Initialize specs and documentation structures in specs/015-additional-drinks-tracking/
- [x] T002 Verify local simulation server runs successfully on port 3000

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema and simulation database support that MUST be complete before ANY user story can be implemented

- [x] T003 Seed the local JSON database template in web/web_local_db.json with zeroed counters for Martini, G+T, Negroni, and Port

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add Secure Logging for New Drinks on Admin Portal (Priority: P1) 🎯 MVP

**Goal**: Add logging capability for Martini, G+T, Negroni, and Port on the participant's manual admin logging panel.

**Independent Test**: Load the admin panel `/admin.html?u=cha`, save Charlotte's secure key, and verify that the rows for Martini, G+T, Negroni, and Port display correctly and log data on "+" button tap.

### Tests for User Story 1 (OPTIONAL)

- [x] T004 [P] [US1] Add unit tests in backend/tests/unit/test_math_helpers.py to verify that logging any of the new drinks correctly aggregates total_drinks but does not increment beer_drinks

### Implementation for User Story 1

- [x] T005 [P] [US1] Add responsive logging button rows for Martini, G+T, Negroni, and Port in web/admin.html inside the Drinks Counter panel
- [x] T006 [P] [US1] Add category mapping and floor boundaries logic for Martini, G+T, Negroni, and Port in web/js/admin.js

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Conditional Public Dashboard Drinks Breakdown (Priority: P2)

**Goal**: Render a detailed drinks breakdown on the public dashboard displaying individual consumed drinks if and only if more than 1 of that drink category has been consumed.

**Independent Test**: Update database categories to show Negroni: 2, Port: 3, G+T: 1. Load the public dashboard `/index.html?u=cha` and verify only Negroni and Port are rendered in the breakdown section.

### Tests for User Story 2 (OPTIONAL)

- [x] T007 [P] [US2] Add integration test coverage in backend/tests/integration/test_playback_flow.py to assert that multi-user event-sourced playback correctly compiles tallies for Negroni and Port

### Implementation for User Story 2

- [x] T008 [P] [US2] Add HTML container structure for "Drinks Breakdown" in web/index.html under the Drinks Intake section
- [x] T009 [P] [US2] Implement conditional client-side filtering logic (count >= 2) and dynamic list rendering in web/js/app.js
- [x] T010 [P] [US2] Implement zero-state placeholder message handling in web/js/app.js for when no drink counts exceed 1

**Checkpoint**: At this point, User Stories 1 and 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Live Admin Sync & State Verification (Priority: P3)

**Goal**: Synchronize live counts of Martini, G+T, Negroni, and Port when clicking the "Sync State" button on the admin panel.

**Independent Test**: Click "Sync State" on the admin panel and confirm all new categories reflect the correct database state.

### Implementation for User Story 3

- [x] T011 [P] [US3] Extend syncState() and updateDisplayCount() functions in web/js/admin.js to map and synchronize Martini, G+T, Negroni, and Port

**Checkpoint**: All user stories are now fully functional and verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and validation checks across all components

- [x] T012 Run the quickstart.md validation guide scenarios end-to-end to confirm feature success
- [x] T013 Run full Python test suites and ensure coverage gates are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 Setup.
- **User Stories (Phase 3+)**: All depend on Foundational (Phase 2) completion.
  - User Story 1 (P1) is the blocker for US2/US3 end-to-end flow.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Within Each User Story

- Frontend layout designs before JS controller integrations.
- API simulation checks before public dashboard visual renders.

### Parallel Opportunities

- All tasks marked with **[P]** can be implemented and tested concurrently since they occupy independent files and layers.

---

## Parallel Example: User Story 1

```bash
# Developer A (Frontend Admin Layout):
Task: "Add responsive logging button rows for Martini, G+T, Negroni, and Port in web/admin.html"

# Developer B (Backend Unit/Math Testing):
Task: "Add unit tests in backend/tests/unit/test_math_helpers.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational database seeder tasks.
2. Complete User Story 1 to allow the actual logging of Martini, G+T, Negroni, and Port.
3. Validate logging manually with simulator server active.

### Incremental Delivery

1. Setup + Foundational -> Project and DB structures ready.
2. User Story 1 (MVP) -> Recording beverages is functional.
3. User Story 2 -> Dynamic breakdown display is functional.
4. User Story 3 -> Live bidirectionality is functional.
5. Polish -> Quickstart verification passes.
