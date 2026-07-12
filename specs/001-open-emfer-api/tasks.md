# Tasks: Open EMF Camper API

**Input**: Design documents from `specs/001-open-emfer-api/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included below as mandated by the automated testing standard of the Constitution (Principle VI).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Codebase structured as a decoupled Python/Terraform project under `backend/` and `tf/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure under `backend/` and `tf/` per implementation plan `specs/001-open-emfer-api/plan.md`
- [x] T002 Initialize Python project with ruff configuration in `backend/pyproject.toml`
- [x] T003 [P] Setup basic Terraform provider structure in `tf/main.tf`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Setup DynamoDB single-table composite key schema using Terraform in `tf/dynamodb.tf`
- [x] T005 [P] Setup AWS Secrets Manager variables inside `tf/secrets.tf`
- [x] T006 [P] Implement authorization helper and standard logging utilities in `backend/lambdas/utils.py`
- [x] T007 Configure local pytest framework and DynamoDB mocking configuration in `backend/tests/conftest.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Log Camper Telemetry (Priority: P1) 🎯 MVP

**Goal**: Authenticated real-time logging of drinks, statuses, and activities (POST `/beer`) with support for undo/offset reversals.

**Independent Test**: Perform an authorized POST request containing telemetry parameters to `/beer` and verify that the raw log is created with a UUID and categories are correctly updated/decremented in the aggregates table.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Write unit test for standard drink log increment in `backend/tests/unit/test_beer_handler.py`
- [x] T009 [P] [US1] Write unit test for offset logging reversal under `"reverse": true` in `backend/tests/unit/test_beer_handler.py`
- [x] T010 [P] [US1] Write unit test for unauthorized logging request rejection in `backend/tests/unit/test_beer_handler.py`

### Implementation for User Story 1

- [x] T011 [US1] Implement incoming request validation matching JSON contract `beer-post.json` inside `backend/lambdas/beer_handler/handler.py`
- [x] T012 [US1] Implement telemetry aggregate accounting (increment/decrement) and raw log write logic in `backend/lambdas/beer_handler/handler.py`
- [x] T013 [US1] Deploy Lambda handler and POST `/beer` endpoint integrations using Terraform in `tf/lambdas.tf` and `tf/api_gateway.tf`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Retrieve Dashboard Statistics (Priority: P1)

**Goal**: Public retrieval of current statistics, statuses, and location histories via GET `/beer` and GET `/history`.

**Independent Test**: Run GET `/beer?event=drinks` or GET `/history` and confirm retrieval of consolidated aggregate objects matching schema contracts.

### Tests for User Story 2

- [x] T014 [P] [US2] Write unit test for drink totals retrieval schema compliance in `backend/tests/unit/test_beer_handler.py`
- [x] T015 [P] [US2] Write unit test for location history retrieval in `backend/tests/unit/test_beer_handler.py`

### Implementation for User Story 2

- [x] T016 [US2] Implement drink metrics consolidated sum and status response resolver in `backend/lambdas/beer_handler/handler.py`
- [x] T017 [US2] Implement location history sequence (max 20 entries) and travel totals fetcher in `backend/lambdas/beer_handler/handler.py`
- [x] T018 [US2] Deploy GET `/beer` and GET `/history` API routes in `tf/api_gateway.tf`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - LoRa IoT Device Ingestion (Priority: P2)

**Goal**: Capture environmental temperature, light, and sound updates from T1000 and Browan LoRa devices.

**Independent Test**: Send authorized mock sensor payloads to `/sensecap` and `/browan` and verify Haversine distance changes and sound updates in the database.

### Tests for User Story 3

- [x] T019 [P] [US3] Write unit test for Haversine distance calculations and stride-based step mapping in `backend/tests/unit/test_sensecap_ingest.py`
- [x] T020 [P] [US3] Write unit test for Browan decibel level recording in `backend/tests/unit/test_browan_ingest.py`

### Implementation for User Story 3

- [x] T021 [P] [US3] Implement Haversine mathematical distance solver and step-length estimators in `backend/lambdas/utils.py`
- [x] T022 [US3] Implement T1000 GPS ingestion and location history array limits (max 20 entries) inside `backend/lambdas/sensecap_ingest/handler.py`
- [x] T023 [US3] Implement Browan sound telemetry decibel tracking in `backend/lambdas/browan_ingest/handler.py`
- [x] T024 [US3] Deploy `/sensecap` and `/browan` API ingestion handlers using Terraform in `tf/lambdas.tf` and `tf/api_gateway.tf`

**Checkpoint**: User Stories 1, 2, and 3 should now be independently functional

---

## Phase 6: User Story 4 - Bank Transaction Monitoring (Priority: P3)

**Goal**: Asynchronous background Monzo transaction ingestion and formatting.

**Independent Test**: Trigger Monzo sync Lambda, check formatted outputs for credits, and query GET `/monzo` to ensure list outputs are successful.

### Tests for User Story 4

- [x] T025 [P] [US4] Write unit test for dynamic Monzo OAuth credential retrieval from Secrets Manager in `backend/tests/unit/test_monzo_sync.py`
- [x] T026 [P] [US4] Write unit test verifying that positive deposit credits are parsed with a `(CREDIT)` tag in `backend/tests/unit/test_monzo_sync.py`

### Implementation for User Story 4

- [x] T027 [US4] Implement AWS Secrets Manager loading and Monzo API polling loops in `backend/lambdas/monzo_sync/handler.py`
- [x] T028 [US4] Implement transaction cents-to-pounds currency division and Credit formatting in `backend/lambdas/monzo_sync/handler.py`
- [x] T029 [US4] Implement cached GET `/monzo` transaction database read handler inside `backend/lambdas/monzo_sync/handler.py`
- [x] T030 [US4] Configure scheduled EventBridge rule sync (cron) and deploy GET `/monzo` endpoint with Terraform in `tf/lambdas.tf` and `tf/api_gateway.tf`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T031 Align root-level contract schemas in `openapi.json` with final API Gateway route deployments
- [x] T032 Run PEP 8 style checks and formatting validations using ruff inside `backend/`
- [x] T033 Verify Terraform stack validations using `terraform validate` inside `tf/`
- [x] T034 Run full test suite with `pytest` inside `backend/`
- [x] T035 [P] Run curl validation tests defined in `specs/001-open-emfer-api/quickstart.md` on deployed infrastructure

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1's schema mapping, but can proceed after Phase 2 as an independent reading module
- **User Story 3 (P3)**: Depends on Phase 2 base infrastructure, can run independently
- **User Story 4 (P4)**: Depends on Phase 2 base infrastructure, can run independently

---

## Parallel Example: User Story 1

```bash
# Launch unit tests for User Story 1 together:
pytest backend/tests/unit/test_beer_handler.py -k "increment or reversal"

# Initialize utilities and configuration variables simultaneously:
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
5. Add User Story 4 → Test independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Verify tests fail before implementing
- Commit after each task or logical group
