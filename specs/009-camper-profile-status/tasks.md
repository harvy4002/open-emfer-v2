# Tasks: Camper Profile Status Photos

**Input**: Design documents from `/specs/009-camper-profile-status/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Unit tests are not requested in the specification; validation will be conducted interactively using the local Python socket simulator and the Quickstart Validation scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verifying local directory layouts and assets

- [X] T001 Verify that the pre-existing user-uploaded status assets folder `web/harvy_status/` exists and contains the required 11 `.jpg` files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Preparing fallback assets and CSS visual container styles

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Verify or copy a default profile picture fallback asset (e.g., a generic avatar) to `web/harvy_status/harvy_normal.jpg` as the root baseline fallback image
- [X] T003 Define CSS aspect ratio and crop properties (`object-fit: cover; max-height: 250px;`) on the `#camper-status-image` container inside `web/index.html` to prevent layout shifts across photo dimensions

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Dynamic Harvy Status Avatar (Priority: P1) 🎯 MVP

**Goal**: Automatically map Harvy's real-time telemetry status to the corresponding `.jpg` in `web/harvy_status/`

**Independent Test**: Put the simulator or logger into "sleeping" state for user `hvy`. Verify that the dashboard profile picture box displays `/harvy_status/harvy_sleeping.jpg`.

### Implementation for User Story 1

- [X] T004 [US1] Modify the `#camper-status-image` DOM element in `web/index.html` to include a native HTML `onerror` handler that seamlessly replaces the source with `/harvy_status/harvy_normal.jpg` upon load failure
- [X] T005 [US1] Remove or comment out the hardcoded `STATUS_IMAGES` lookup dictionary mapping external Unsplash URLs inside `web/js/app.js`
- [X] T006 [US1] Implement dynamic path string interpolation inside `web/js/app.js` to map `statusText` to lowercase and resolve the file route `/${activeUser}_status/${activeUser}_${statusText.toLowerCase()}.jpg`
- [X] T007 [US1] Bind the resolved dynamic URL to the `#camper-status-image` element's `src` attribute inside the telemetry update success callback of `web/js/app.js`

**Checkpoint**: At this point, Harvy's dashboard dynamic photo status changes are fully operational and testable independently.

---

## Phase 4: User Story 2 - Multi-Camper Provision (Priority: P2)

**Goal**: Enable identical dynamic status mappings for other campers (`cha`, `ash`, `tin`) utilizing their own status sub-folders

**Independent Test**: Load Charlotte's dashboard (`u=cha`), trigger the "coding" status, and verify that `/cha_status/cha_coding.jpg` renders successfully.

### Implementation for User Story 2

- [X] T008 [US2] Update the native `onerror` handler of `#camper-status-image` in `web/index.html` to dynamically construct the fallback path based on the active user (i.e. replacing with `/${activeUser}_status/${activeUser}_normal.jpg`) rather than hardcoding Harvy's folder
- [X] T009 [US2] Implement a secondary fallback script in `web/js/app.js` to load a default global profile avatar `/web/harvy_status/harvy_normal.jpg` if the current user's `_normal.jpg` itself fails to load (e.g. if the user has no custom folder)

**Checkpoint**: At this point, Charlotte, Ash, and Tina's dashboards work independently and fallback gracefully.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: General responsive testing and documentation updates

- [X] T010 Validate that all 11 of Harvy's pre-existing photo statuses (drinking, eating, lecture, wet, workshop, normal, etc.) load flawlessly when simulated
- [X] T011 Verify responsive layout widths down to 320px width on mobile viewports using Chrome DevTools with zero horizontal scroll
- [X] T012 Run and complete the entire `specs/009-camper-profile-status/quickstart.md` validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3 & 4)**: All depend on Foundational phase completion
  - User Story 1 (P1) is the MVP and must be completed first
  - User Story 2 (P2) builds on the routing structures of US1
- **Polish (Final Phase)**: Depends on all user stories being complete

### Parallel Opportunities

- Verification of assets layout (T001) can run in parallel with fallback asset generation (T002).
- Native inline `onerror` fallback setup (T004) can run in parallel with the js deprecation (T005).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Harvy's dynamic status photos)
4. **STOP and VALIDATE**: Verify Harvy's dashboard with different simulated statuses

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Charlotte, Ash, Tina support)
4. Run Polish & validation checklist
