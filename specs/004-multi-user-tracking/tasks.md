# Tasks: Multi-User Tracking

**Input**: Design documents from `specs/004-multi-user-tracking/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included below as mandated by the automated testing standard of the Constitution (Principle VI).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Codebase structured as a decoupled Python/Terraform project under `backend/`, `web/`, and `tf/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure updates

- [ ] T001 Configure custom CSS variables for mobile-first vertical column stacking and 48px touch targets in `web/css/style.css`
- [ ] T002 Add mock telemetry profiles and test user datasets in `backend/tests/mocks/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Update DynamoDB access helpers in `backend/lambdas/utils.py` to handle Partition Keys structured as `camper#aggregates#<user_id>` or `device#<device_id>#<user_id>`
- [ ] T004 [P] Update token verification helper in `backend/lambdas/utils.py` to support profile-specific writes safely

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Personalized Admin Logger (Priority: P1) 🎯 MVP

**Goal**: Authenticated real-time logging of drinks, statuses, and activities for a specific user using a mobile-first, touch-friendly UI.

**Independent Test**: Load `/admin.html?u=ali` on a standard mobile browser, verify that all button heights are a minimum of 48px with clear tap feedback, click "Log Lager", and verify that Alice's personal aggregates in DynamoDB increment.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T005 [P] [US1] Write unit test for `POST /beer` with custom `user_id` parameter inside `backend/tests/unit/test_beer_handler.py`
- [ ] T006 [P] [US1] Write unit test verifying dual-writing to individual and combined aggregate partitions in `backend/tests/unit/test_beer_handler.py`

### Implementation for User Story 1

- [ ] T007 [US1] Update `POST /beer` handler in `backend/lambdas/beer_handler/handler.py` to parse `user_id` (defaulting to `hvy`) and perform dual-writes to the individual user aggregates and the combined partition
- [ ] T008 [US1] Update the request validation mapping inside `backend/lambdas/beer_handler/handler.py` to accept the `user_id` parameter
- [ ] T009 [US1] Update `admin.html` to parse the compact `u` query parameter and bind it to form submissions and `localStorage` session caching
- [ ] T010 [US1] Configure the profile switcher dropdown in `admin.html` to allow toggling active loggers
- [ ] T011 [US1] Implement the 500ms client-side double-tap throttle inside `web/js/admin.js` to prevent duplicate logs
- [ ] T012 [US1] Apply Bulma CSS column vertical stacking styles and 48px tactile heights in `admin.html` and `web/css/style.css`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Individual Camper Dashboard (Priority: P1)

**Goal**: View a specific camper's public telemetry dashboard (e.g. `/index.html?u=ali`) on a mobile phone with zero layout overflows.

**Independent Test**: Navigate to `/index.html?u=ali` on a mobile browser and confirm that all text counters, active status badges, and Chart.js canvases scale down cleanly to mobile columns with zero overlapping text.

### Tests for User Story 2

- [ ] T013 [P] [US2] Write unit test for `GET /beer?user_id=ali` and `GET /history?user_id=ali` inside `backend/tests/unit/test_beer_handler.py`

### Implementation for User Story 2

- [ ] T014 [US2] Update GET routes in `backend/lambdas/beer_handler/handler.py` to support user-filtered queries
- [ ] T015 [US2] Update `web/js/app.js` to parse `u` query parameter, bind context, and fetch filtered results
- [ ] T016 [US2] Apply mobile-first column restructuring and canvas container aspect ratios in `index.html`
- [ ] T017 [US2] Implement client-side connection warning and status banners in `web/js/app.js`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Combined Leaderboard & Totals (Priority: P2)

**Goal**: View a combined stats dashboard displaying sum totals across all users, alongside a user leaderboard, on a mobile phone.

**Independent Test**: Load `/index.html` (with no user parameter) or `/index.html?u=combined` on a phone and verify that the numeric tiles display the combined sum of Alice's and Harvy's drinks.

### Tests for User Story 3

- [ ] T018 [P] [US3] Write unit test for combined aggregate retrieval `GET /beer?user_id=combined` inside `backend/tests/unit/test_beer_handler.py`

### Implementation for User Story 3

- [ ] T019 [US3] Implement combined aggregate fetcher returning consolidated categories sums and leaderboard ranking array in `backend/lambdas/beer_handler/handler.py`
- [ ] T020 [US3] Update `index.html` to hide individual environmental charts when `?u=combined` is loaded
- [ ] T021 [US3] Render dynamic leaderboard and combined sum tiles in `web/js/app.js`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T022 [P] Regenerate/Validate physical QR codes using short URL parameters and test scan locking times
- [ ] T023 Run PEP 8 formatting check on `backend/lambdas/` using ruff
- [ ] T024 Run test suite to verify 100% test coverage using pytest
- [ ] T025 [P] Run curl validation commands in `specs/004-multi-user-tracking/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

---

## Parallel Example: User Story 1

```bash
# Launch unit tests for User Story 1 together:
pytest backend/tests/unit/test_beer_handler.py -k "increment or reversal"

# Initialize variables simultaneously:
# T005 [P] and T006 [P] can run concurrently
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently via local mocks
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently
4. Add User Story 3 → Test independently
