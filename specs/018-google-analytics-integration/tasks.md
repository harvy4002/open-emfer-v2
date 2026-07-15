# Tasks: Google Analytics Integration

**Input**: Design documents from `/specs/018-google-analytics-integration/`

**Prerequisites**: plan.md (required), spec.md (required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project and workspace environment initialization

- [x] T001 Verify active specifications context under specs/018-google-analytics-integration/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core client-side configuration file structure that MUST be complete before ANY user story can be implemented

- [x] T002 Create the standard centralized configuration file web/js/config.js containing the EMF_CONFIG global variable block with placeholder G-XXXXXXXXXX key

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Centralized Analytics Configuration (Priority: P1) 🎯 MVP

**Goal**: Load the central configuration file globally into the public dashboard ahead of any other execution script blocks.

**Independent Test**: Load the public dashboard index `/index.html?u=cha` and confirm browser loads config.js successfully in correct order.

### Implementation for User Story 1

- [x] T003 [P] [US1] Inject config.js script tag inside web/index.html head above the core app.js import

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Dynamic Analytics Script Injection (Priority: P2)

**Goal**: Implement dynamic gtag.js script loading and configuration on dashboard loads.

**Independent Test**: Configure a valid GA key in `config.js` and verify Google site tag elements append to document head on load.

### Implementation for User Story 2

- [x] T004 [P] [US2] Implement dynamic script tag compilation and head insertion routine in web/js/app.js
- [x] T005 [P] [US2] Implement global window.dataLayer and gtag('config') initialization in web/js/app.js

**Checkpoint**: At this point, User Stories 1 and 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Graceful Analytics Bypass (Priority: P3)

**Goal**: Implement strict placeholder and empty string bypass gates to prevent analytics tracking in unconfigured environments.

**Independent Test**: Clear the GA key in `config.js` and verify no googletagmanager script tag is loaded.

### Implementation for User Story 3

- [x] T006 [P] [US3] Add empty string and G-XXXXXXXXXX pattern bypass gates inside web/js/app.js dynamic injection loop

**Checkpoint**: All user stories are now fully functional and verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and validation checks across all components

- [x] T007 Run the quickstart.md validation guide scenarios end-to-end to confirm feature success
- [x] T008 Run full Python test suites to ensure complete codebase health and zero regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 Setup.
- **User Stories (Phase 3+)**: All depend on Foundational (Phase 2) completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- All tasks marked with **[P]** can be implemented and tested concurrently since they occupy independent files and layers.
