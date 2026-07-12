# Tasks: Participant Admin Portal

**Input**: Design documents from `/specs/007-participant-admin-portal/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Static assets: `web/admin.html` and `web/js/admin.js`
- Local simulator server: `backend/sim_server.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure verification.

- [X] T001 Create feature-specific documentation directories and checklist index files in `specs/007-participant-admin-portal/`
- [X] T002 [P] Verify existing local assets structure and ensure backend simulator can serve `web/admin.html` in `backend/sim_server.py`
- [X] T003 [P] Verify code styles and lint configurations for standard JavaScript in `web/js/admin.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Configure the local simulator endpoints in `backend/sim_server.py` to support query filters and ensure that standard GET and POST requests are mocked correctly
- [X] T005 [P] Establish local storage caching hooks for credentials (`admin_tracker_key` and `active_user_id`) in `web/js/admin.js`
- [X] T006 [P] Set up base client router parsing to dynamically resolve backend host URL (`API_BASE`) in `web/js/admin.js`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Secure Telemetry Logging (Priority: P1) 🎯 MVP

**Goal**: Secure manual logging of drinks, toilet visits, status, and reset transactions via authenticated POST calls with headers.

**Independent Test**: Navigate to `/admin.html`, enter a valid `tracker_key`, click log, and confirm request includes header and returns 201.

- [X] T007 [US1] Implement secure token key input form and save/load callbacks inside `web/admin.html`
- [X] T008 [US1] Implement authorization key caching and validation inside `web/js/admin.js`
- [X] T009 [US1] Update POST request headers to inject the cached `tracker_key` inside `web/js/admin.js`
- [X] T010 [US1] Implement interactive feedback flash banner displays inside `web/admin.html` and `web/js/admin.js`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Personalized Mobile-First Field Logging (Priority: P1)

**Goal**: High-contrast, vertically stacking logging targets with tactile 48px sizes dynamically associated with the parsed camper shortcode.

**Independent Test**: Load `/admin.html?u=ali` on mobile DevTools (360px), tap lager, and verify payload contains `"user_id": "ali"`.

- [X] T011 [US2] Apply responsive Bulma column vertical stacking styles and standard mobile scaling in `web/admin.html`
- [X] T012 [US2] Update button tap targets and form fields to maintain a minimum of 48px tactile height in `web/admin.html`
- [X] T013 [US2] Implement URL search parameter extraction to resolve the `u` parameter on load in `web/js/admin.js`
- [X] T014 [US2] Update all telemetry submission payload structures to inject the resolved `user_id` context inside `web/js/admin.js`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Camper-Specific Link Locking (Priority: P2)

**Goal**: Enforce strict user session locking, eliminating profile dropdown swappers from individual devices to prevent cross-camper logging errors.

**Independent Test**: Load `/admin.html?u=ali`, verify no dropdown swapper is visible, and the header shows "Alice Smith's Logging Portal".

- [X] T015 [US3] Remove or dynamically hide the profile selection dropdown inside `web/admin.html` when a user context is locked
- [X] T016 [US3] Implement hardcoded camper name mappings (`hvy`, `ali`, `bob`) inside `web/js/admin.js`
- [X] T017 [US3] Update the page header dynamically to show the locked camper's full display name inside `web/admin.html` and `web/js/admin.js`
- [X] T018 [US3] Implement query fallback parsing to default to `hvy` if parameter `u` is missing inside `web/js/admin.js`

**Checkpoint**: User Stories 1, 2, and 3 should now be functional and locked.

---

## Phase 6: User Story 4 - Live Value Display & Bi-Directional Counter Controls (Priority: P1)

**Goal**: Retrieve and display live counts alongside tactile "+" and "-" buttons, calling the backend with `reverse: true` for corrections.

**Independent Test**: Load `/admin.html?u=ali`, tap "+", verify count goes up. Tap "-", verify count goes down via API and locks at `0`.

- [X] T019 [US4] Implement layout containers to display live count values adjacent to each item in `web/admin.html`
- [X] T020 [US4] Implement the GET state fetch requests to load active drinks and steps telemetry on load in `web/js/admin.js`
- [X] T021 [US4] Add explicit "-" (decrement) button controls next to each incrementable metric inside `web/admin.html`
- [X] T022 [US4] Implement increment ("+") and decrement ("-") event handler callbacks inside `web/js/admin.js`
- [X] T023 [US4] Integrate `"reverse": true` parameter logic inside the telemetry logging payload inside `web/js/admin.js`
- [X] T024 [US4] Implement zero-value floor lock protection to disable the "-" buttons when a count is `0` inside `web/js/admin.js`
- [X] T025 [US4] Implement a manual "Sync" refresh button control to update state on demand in `web/admin.html` and `web/js/admin.js`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [X] T026 [P] Apply client-side 500ms tap throttle/prevention across all "+" and "-" buttons in `web/js/admin.js`
- [X] T027 [P] Document and clean up formatting and console logging statements inside `web/js/admin.js`
- [X] T028 [P] Update project-wide memory and documentation files to note completion of Phase 1-6 tasks
- [X] T029 Execute all validation scenarios specified in `specs/007-participant-admin-portal/quickstart.md` using the local python simulation environment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User stories proceed in priority order (US1 → US2 → US4 → US3).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories.
- **User Story 2 (P1)**: Can start after US1 - integrates with secure token key prompts.
- **User Story 4 (P1)**: Can start after US2 - relies on personalized context binding to fetch counts.
- **User Story 3 (P2)**: Can start after US4 - locks the profile context completely.

---

## Parallel Execution Opportunities

- Setup tasks `T002` and `T003` can run in parallel.
- Foundational tasks `T005` and `T006` can run in parallel.
- Polish tasks `T026`, `T027`, and `T028` can run in parallel once US4 is implemented.

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
4. Add User Story 4 → Test independently → Deploy/Demo.
5. Add User Story 3 → Test independently → Deploy/Demo.
