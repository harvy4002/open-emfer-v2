# Tasks: Grafana-Style Public Dashboard and Participant Admin

**Input**: Design documents from `specs/002-public-dashboard/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Scenario testing is handled via browser-native testing scripts as defined in `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Codebase structured as a decoupled static assets project under `web/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize the `web/css/style.css` with Bulma CDN overrides and Grafana theme variables
- [x] T002 Initialize the `web/js/app.js` and `web/js/admin.js` scripts
- [x] T003 Initialize the HTML skeletons for `web/index.html` and `web/admin.html`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 Implement DOM binding ID structures matching `contracts/dom-elements.json`
- [x] T005 Implement `localStorage` helpers for preferences matching `contracts/localstorage-schemas.json`

---

## Phase 3: User Story 1 - Live Public Dashboard Access (Priority: P1)

**Goal**: A dark-theme, grid-based dashboard inspired by Grafana's multi-panel visualizer.

### Implementation for User Story 1

- [x] T006 [US1] Build the HTML layout grids with Bulma CSS in `web/index.html`
- [x] T007 [US1] Implement Chart.js canvases and responsive wrappers in `web/index.html`
- [x] T008 [US1] Implement `fetch()` logic to pull live metrics in `web/js/app.js`
- [x] T009 [US1] Implement the Visibility API throttling and network jitter timeouts in `web/js/app.js`
- [x] T010 [US1] Implement offline connection warning banners and stale state handling in `web/js/app.js`

---

## Phase 4: User Story 2 - Participant Admin Logging (Priority: P1)

**Goal**: An authenticated admin interface prompting campers for the `tracker_key` and exposing forms.

### Implementation for User Story 2

- [x] T011 [US2] Build the form panels and submission buttons in `web/admin.html`
- [x] T012 [US2] Implement the `tracker_key` prompt and local storage persistor in `web/js/admin.js`
- [x] T013 [US2] Implement API POST logic for drinks, statuses, and reset triggers in `web/js/admin.js`
- [x] T014 [US2] Add the reverse logging toggle checkbox and binding logic in `web/admin.html` and `web/js/admin.js`

---

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T015 Verify CSS responsiveness on mobile viewports
- [x] T016 Run Quickstart scenario validation tests
