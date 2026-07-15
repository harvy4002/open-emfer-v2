# Tasks: Browser Notifications Scheduler

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

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Since this feature operates 100% client-side with zero backend/database dependencies, we skip server-side foundation stages.

- [x] T002 Verify standard browser Notification API is available in active web sandbox environments

**Checkpoint**: Core foundation checked - user story implementation can now begin

---

## Phase 3: User Story 1 - Notification Subscription Switch (Priority: P1) 🎯 MVP

**Goal**: Render the toggle switch panel and implement the standard W3C Notification permission requesting and localStorage caching.

**Independent Test**: Load `/admin.html?u=cha` and toggle the notification switch to "On". Grant permissions and confirm local storage caches `"true"`.

### Implementation for User Story 1

- [x] T003 [P] [US1] Create the Bulma-styled panel structure and toggle switch inside web/admin.html for the notifications settings card
- [x] T004 [P] [US1] Implement change listeners, W3C permissions requesting Notification.requestPermission() and localStorage caching of subscription states inside web/js/admin.js

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Customizable Reminder Interval Dropdown (Priority: P2)

**Goal**: Implement customizable scheduler loops and intervals using standard background `setInterval` timers.

**Independent Test**: Select "1 Minute (Test Option)", minimize the tab, and confirm a notification is delivered 60 seconds later.

### Implementation for User Story 2

- [x] T005 [P] [US2] Add the dropdown select element mapping the configurable intervals inside web/admin.html next to the toggle switch
- [x] T006 [P] [US2] Implement active interval select change handlers and setInterval scheduling loops inside web/js/admin.js
- [x] T007 [P] [US2] Implement global interval timer teardown and clearInterval() cleanup logic on unsubscribe/disable in web/js/admin.js

**Checkpoint**: At this point, User Stories 1 and 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Interactive Focus and Portal Launch (Priority: P3)

**Goal**: Override the `onclick` handler of the generated `Notification` instance to bring `/admin.html` immediately to the foreground.

**Independent Test**: Tap the fired notification and verify it instantly refocuses the Logging Portal.

### Implementation for User Story 3

- [x] T008 [P] [US3] Add the on-click focus handler window.focus() on generated standard Notification object instances inside web/js/admin.js

**Checkpoint**: All user stories are now fully functional and verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and validation checks across all components

- [x] T009 Run the quickstart.md validation guide scenarios end-to-end to confirm feature success
- [x] T010 Run full Python test suites to ensure complete codebase health and zero regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 Setup.
- **User Stories (Phase 3+)**: All depend on Foundational (Phase 2) completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- All tasks marked with **[P]** can be implemented and tested concurrently since they occupy independent files and layers.
