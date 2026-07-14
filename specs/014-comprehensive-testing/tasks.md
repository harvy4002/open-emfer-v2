# Tasks: Comprehensive Test Coverage

**Input**: Design documents from `specs/014-comprehensive-testing/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Explicit file paths are included in descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and loading external Leaflet/coverage assets.

- [X] T001 Configure/Verify backend testing dependencies (`coverage`, `pytest`, `pytest-cov`) inside the development sandbox.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and base setup.

- [X] T002 Ensure that the existing backend integration test script (`backend/test_endpoints.py`) can execute successfully on local sandbox port 3000.

---

## Phase 3: User Story 1 - Unit Testing of Backend Logic & Utility Primitives (Priority: P1)

**Goal**: Write unit tests verifying core logic primitives (Haversine calculations, step translation, and status text mapping).

**Independent Test**: Run python unit tests inside `backend/tests/unit/` using pytest; check that all calculation assertions succeed offline.

### Implementation for User Story 1

- [X] T003 [P] [US1] Create unit tests for Haversine walking distance calculation and stride-based step mapping in `backend/tests/unit/test_math_helpers.py`, ensuring 100% test coverage targets.
- [X] T004 [P] [US1] Create unit tests for status photo name mapping and keyword-matching resolution inside `backend/tests/unit/test_status_resolver.py`.

**Checkpoint**: Core math and resolution helpers are fully unit-tested with 100% coverage.

---

## Phase 4: User Story 2 - Integration Testing of Endpoint Chains (Priority: P2)

**Goal**: Ensure all simulation handlers and event replay endpoints (/playback, /history, /beer) have extensive integration testing hitting 80%+ overall coverage.

**Independent Test**: Run backend code coverage and verify overall python backend handlers code coverage is 80%+.

### Implementation for User Story 2

- [X] T005 [US2] Implement integration test coverage for the `/playback` endpoint event replay flow in `backend/tests/integration/test_playback_flow.py`, validating chronological event state reconstruction.
- [X] T006 [US2] Implement integration test coverage for `/history` and `/sensecap` multi-user simulation steps inside `backend/tests/integration/test_history_flow.py`.
- [X] T007 [US2] Configure `.coveragerc` or inline parameters in the backend test scripts to exclude system/third-party imports and verify overall code coverage gates.

**Checkpoint**: Backend simulation handlers are fully covered above the 80% coverage threshold.

---

## Phase 5: User Story 3 - Browser/End-to-End Testing of Dashboard and Simulator Views (Priority: P3)

**Goal**: Build a lightweight standalone DOM visual runner inside `web/test_suite.html` asserting map rendering and canvas initialization.

**Independent Test**: Load `web/test_suite.html` in any browser; check that 100% of DOM and Leaflet/ChartJS assertions render as passing.

### Implementation for User Story 3

- [X] T008 [P] [US3] Create the basic HTML layout and UI test result card structure for the standalone test runner inside `web/test_suite.html`.
- [X] T009 [US3] Implement browser-native `fetch()` API intercepts and mock response generators inside `web/test_suite.html` to return mock JSON arrays for `/history` and `/beer`.
- [X] T010 [US3] Define sandboxed DOM target elements (`#map-container` map layer, `#temperature-chart-canvas`, `#stepsVal`) inside `web/test_suite.html`.
- [X] T011 [US3] Write client-side JS assertions inside `web/test_suite.html` verifying that the Leaflet map correctly instantiates, binds tile error fallbacks, and Chart.js mounts temperature/noise panels successfully.

**Checkpoint**: All visual frontend components and Leaflet/Chart integrations are fully covered by the DOM assertions suite.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Automation scripts and guides creation.

- [X] T012 Implement `backend/run_tests.py` as a unified python runner that starts the local HTTP server, executes coverage, triggers browser tests report status, and returns corresponding exit codes (`0` on pass, `1` on fail).
- [X] T013 Create a detailed test runner guide or update `README.md` explaining how to execute code coverage checks and view the visual browser test suite.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User stories then proceed in sequence (P1 → P2 → P3).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

```text
+---------------+
| Phase 1 Setup |
+---------------+
        |
        v
+----------------------+
| Phase 2 Foundational |
+----------------------+
        |
        +----------------------------+
        |                            |
        v                            v
+--------------------------+  +--------------------------+
| Phase 3 User Story 1 (P1)|  | Phase 5 User Story 3 (P3)|
+--------------------------+  +--------------------------+
        |
        v
+--------------------------+
| Phase 4 User Story 2 (P2)|
+--------------------------+
        |
        v
+--------------------------+
|   Phase 6 Polish & E2E   |
+--------------------------+
```

### Parallel Opportunities

- Unit tests (**T003**, **T004**) can run in parallel (different files).
- Browser tests setup (**T008**) can be prepared concurrently with the unit test implementations.

---

## Parallel Example: Core Logic & DOM Setup

```bash
# Developer A: Implement math helper unit tests
Task: "Create unit tests for Haversine walking distance calculation and stride-based step mapping in backend/tests/unit/test_math_helpers.py"

# Developer B: Create DOM visual test structure
Task: "Create the basic HTML layout and UI test result card structure inside web/test_suite.html"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1 (Critical primitives 100% covered).
4. Complete Phase 4: User Story 2 (Overall coverage $\ge$ 80%).
5. Validate using `coverage report -m`.

### Incremental Delivery

1. Verify existing local tests runner compatibility → Baseline OK.
2. Add math & keyword-matching unit tests → Verifies backend calculations.
3. Add integration test coverage for `/playback` and `/history` → API handlers verified.
4. Establish overall coverage gates → Code safety locked.
5. Create `test_suite.html` for DOM assertions → Frontend visual integrity verified.
6. Build unified `run_tests.py` automation wrapper → Complete one-click pipeline.
