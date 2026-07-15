# Tasks: Web Push Notification Scheduler

**Input**: Design documents from `/specs/017-browser-notifications-scheduler/`

**Prerequisites**: plan.md (required), spec.md (required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project and workspace environment initialization

- [x] T001 Verify active specifications context under specs/017-browser-notifications-scheduler/
- [x] T002 Add and install pywebpush dependency inside the project environment

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core VAPID key generation and script configurations that MUST be complete before ANY user story can be implemented

- [x] T003 Generate the public and private VAPID keys using python cryptography, and store them securely in backend/sim_server.py
- [x] T004 [P] Store the public VAPID key in window.EMF_CONFIG inside web/js/config.js to allow client-side PushManager bindings

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Web Push Subscription Toggle (Priority: P1) 🎯 MVP

**Goal**: Create manifest, service worker, and subscription API routes, enabling secure context push subscriptions.

**Independent Test**: Load `/admin.html?u=cha` and toggle notifications switch to "On". Confirm that sw.js registers, permissions are requested, and subscription payload POSTs to /push-subscribe successfully.

### Tests for User Story 1

- [x] T005 [P] [US1] Add a unit test in backend/tests/unit/test_math_helpers.py asserting that POSTing to /push-subscribe correctly stores W3C subscription endpoints in Charlotte's aggregates record

### Implementation for User Story 1

- [x] T006 [P] [US1] Create the standard Web App Manifest web/manifest.json and link it inside web/admin.html head to enable mobile PWA notifications capabilities
- [x] T007 [P] [US1] Create the background Service Worker web/sw.js to listen for standard push events and display native notification reminders
- [x] T008 [P] [US1] Refactor subscription switch and W3C PushManager.subscribe() logic inside web/js/admin.js to bind using the public VAPID key
- [x] T009 [P] [US1] Implement the POST /push-subscribe endpoint inside backend/sim_server.py to securely store push subscription JSON tokens in individual camper aggregates

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Customizable Reminder Interval (Priority: P2)

**Goal**: Implement interval setting propagation on the frontend and server-side background schedulers utilizing pywebpush.

**Independent Test**: Select "1 Minute (Test Option)", minimize the tab, and confirm a notification is pushed 60 seconds later.

### Implementation for User Story 2

- [x] T010 [P] [US2] Implement interval select change triggers in web/js/admin.js to instantly POST updated interval preferences to the backend
- [x] T011 [P] [US2] Implement the server-side cron dispatcher background thread (or loop) inside backend/sim_server.py to check and fire pywebpush alerts on interval lapses

**Checkpoint**: At this point, User Stories 1 and 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Interactive Focus and Portal Launch (Priority: P3)

**Goal**: Implement Service Worker click actions to bring `/admin.html` instantly to the foreground.

**Independent Test**: Tap the received notification and verify it focuses the Logging Portal.

### Implementation for User Story 3

- [x] T012 [P] [US3] Add the on-click refocus event listener notificationclick in web/sw.js to bring administrative windows immediately to the foreground

**Checkpoint**: All user stories are now fully functional and verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and validation checks across all components

- [x] T013 Run the quickstart.md validation guide scenarios end-to-end to confirm feature success
- [x] T014 Run full Python test suites to ensure complete codebase health and zero regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 Setup.
- **User Stories (Phase 3+)**: All depend on Foundational (Phase 2) completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- All tasks marked with **[P]** can be implemented and tested concurrently since they occupy independent files and layers.
