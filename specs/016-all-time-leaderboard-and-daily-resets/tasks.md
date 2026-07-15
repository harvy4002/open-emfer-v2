# Tasks: All-Time Leaderboard Steps and Daily Resets

**Input**: Design documents from `/specs/016-all-time-leaderboard-and-daily-resets/`

**Prerequisites**: plan.md (required), spec.md (required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project and workspace environment initialization

- [x] T001 Initialize specs and tasks documentation structures in specs/016-all-time-leaderboard-and-daily-resets/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema support and database seeder upgrades that MUST be complete before ANY user story can be implemented

- [x] T002 Extend the individual aggregate totals seeder in backend/sim_server.py's DEFAULT_DB to support all_time_total_drinks and all_time_cumulative_steps fields
- [x] T003 Extend the combined aggregate totals seeder in backend/sim_server.py's DEFAULT_DB to support steps_leaderboard array and update leaderboard mappings

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - All-Time Beverage Leaderboard (Priority: P1) 🎯 MVP

**Goal**: Track, rank, and render cumulative all-time drink tallies on the combined leaderboard.

**Independent Test**: Load the combined dashboard `/index.html?u=combined` and verify the leaderboard ranks campers by cumulative sums across multiple days.

### Tests for User Story 1

- [x] T004 [P] [US1] Add a unit test in backend/tests/unit/test_math_helpers.py to assert that posting a drink POST aggregates all_time_total_drinks and is unaffected by resetting the daily total
- [x] T005 [P] [US1] Add an integration test in backend/tests/integration/test_playback_flow.py asserting that the combined leaderboard correctly ranks camper positions based on all_time_drinks

### Implementation for User Story 1

- [x] T006 [P] [US1] Modify post API endpoints in backend/sim_server.py to increment all_time_total_drinks in individual aggregates on any new beverage log
- [x] T007 [P] [US1] Update combined aggregate dual-write logic in backend/sim_server.py to map all_time_total_drinks into combined leaderboard array ranks
- [x] T008 [P] [US1] Update the leaderboard renderer in web/js/app.js to display the cumulative all-time drink total on the combined page

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Cumulative All-Time Steps Rankings (Priority: P2)

**Goal**: Maintain, accumulate, and display ranked step count columns on the combined public dashboard.

**Independent Test**: Load the combined dashboard `/index.html?u=combined` and verify that the steps leaderboard accurately lists participants in descending order of cumulative footsteps.

### Implementation for User Story 2

- [x] T009 [P] [US2] Add the HTML layout container structure for "All-Time Steps Leaderboard" in web/index.html next to the drinks leaderboard
- [x] T010 [P] [US2] Update steps API endpoints in backend/sim_server.py to increment and store all_time_cumulative_steps inside individual total records
- [x] T011 [P] [US2] Update combined aggregate calculations in backend/sim_server.py to maintain, sort, and write steps_leaderboard ranks
- [x] T012 [P] [US2] Implement the steps leaderboard visual rendering routine inside web/js/app.js to populate the new steps breakdown cards

**Checkpoint**: At this point, User Stories 1 and 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Automated Daily Participant Stats Reset (Priority: P3)

**Goal**: Automatically trigger a clean slate for daily participant aggregates upon cross-boundary calendar transitions.

**Independent Test**: Shift the aggregate last reset date to yesterday, post a log, and confirm the active counters reset to zero while raw events remain intact.

### Tests for User Story 3

- [x] T013 [P] [US3] Add a unit test in backend/tests/unit/test_math_helpers.py to verify that posting a log on a new day triggers a daily reset event and clears daily active aggregates

### Implementation for User Story 3

- [x] T014 [P] [US3] Implement UTC calendar-day transition lazy check logic inside backend/sim_server.py on mutative POST actions
- [x] T015 [P] [US3] Implement active aggregate clearing (total_drinks, beer_drinks, categories map) and ResetDay event logging on UTC day transitions inside backend/sim_server.py

**Checkpoint**: All user stories are now fully functional and verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification and validation checks across all components

- [x] T016 Run the quickstart.md validation guide scenarios end-to-end to confirm feature success
- [x] T017 Run full Python test suites and ensure coverage gates are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 Setup.
- **User Stories (Phase 3+)**: All depend on Foundational (Phase 2) completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- All tasks marked with **[P]** can be implemented and tested concurrently since they occupy independent files and layers.
