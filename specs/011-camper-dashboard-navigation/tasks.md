# Tasks: Camper Dashboard Quick Navigation

**Input**: Design documents from `/specs/011-camper-dashboard-navigation/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Unit tests are not requested in the specification; validation will be conducted interactively using the local Python socket simulator and the Quickstart Validation scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verifying local development workspace and frontend files

- [X] T001 Verify that `web/index.html` and `web/js/app.js` are fully prepared for navigation updates

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Styling responsive dropdown and horizontal row layouts

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Append a dedicated `#dashboard-navigation-bar` container inside `web/index.html` as the first child of the `#dashboard-view` section
- [X] T003 Setup Bulma CSS helper class layouts inside `web/index.html` to separate desktop/tablet elements (`is-hidden-mobile`) from mobile elements (`is-hidden-tablet`)
- [X] T004 Define mobile select container styles (`.select.is-fullwidth`) in `web/index.html` style block to ensure standard touch bounds and sizing (minimum 48px high)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Quick Dashboard Switching (Priority: P1) 🎯 MVP

**Goal**: Seamlessly transition between user dashboards and return home without full page reloads

**Independent Test**: Navigate to Charlotte's dashboard (`u=cha`). Click the "Tina" button in the navigation header, and verify the page smoothly switches metrics to Tina's dashboard (`u=tin`).

### Implementation for User Story 1

- [X] T005 [US1] Create the horizontal button row inside the desktop-only wrapper (`id="nav-buttons-row"`) in `web/index.html` representing Home, Harvy, Charlotte, Ash, Tina, and Combined
- [X] T006 [US1] Create the matching dropdown select element (`id="nav-mobile-select"`) carrying option keys inside the mobile-only wrapper in `web/index.html`
- [X] T007 [US1] Implement `switchDashboard(camper_id)` inside `web/js/app.js` that pushes new query state using `window.history.pushState` and triggers `initUI()` + telemetry sync callbacks
- [X] T008 [US1] Implement active/inactive tab visual highlight transitions inside `web/js/app.js` (applying `.is-link` vs `.is-dark` to buttons, and updating the selected index of `#nav-mobile-select`)
- [X] T009 [US1] Bind click listeners to desktop nav buttons and change event listeners to mobile `#nav-mobile-select` inside `web/js/app.js` to call `switchDashboard`

**Checkpoint**: At this point, quick navigation switching is fully functional across viewports.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Responsive testing and walkthrough validations

- [X] T010 Test the responsive mobile dropdown layout on Chrome DevTools down to 320px width to ensure 100% viewport alignment and zero horizontal scroll on the main page
- [X] T011 Run and complete the entire `specs/011-camper-dashboard-navigation/quickstart.md` validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3)**: All depend on Foundational phase completion.
- **Polish (Final Phase)**: Depends on all user stories being complete.

### Parallel Opportunities

- HTML template button layout setup (T005) can run in parallel with dropdown layout setup (T006).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Sleek nav headers and dynamic history triggers)
4. Run Polish & validation checklist
