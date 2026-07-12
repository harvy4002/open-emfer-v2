# Tasks: LoRa Telemetry Ingestion

**Input**: Design documents from `specs/003-lora-telemetry-ingestion/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

---

## Phase 1: Setup & Foundation

- [x] T001 Initialize Lambda endpoints folder structure in `backend/lambdas/sensecap_ingest/` and `backend/lambdas/browan_ingest/`
- [x] T002 Implement database composite key abstractions and Secrets Manager retrieval logic

---

## Phase 2: User Story 1 - Ingest and Store T1000 LoRa Telemetry

- [x] T003 [US1] Write test cases for T1000 ingestion in `backend/tests/unit/test_sensecap_ingest.py`
- [x] T004 [US1] Implement `POST /sensecap` handler in `backend/sim_server.py` (and lambda equivalent)
- [x] T005 [US1] Implement JSON payload decoding mapped to `t1000-ingest.json` schema
- [x] T006 [US1] Implement GPS fallback logic: set current coords to null and calculate staleness_seconds
- [x] T007 [US1] Implement 20-entry maximum bounding limit on `location_history` array

---

## Phase 3: User Story 2 - Ingest and Store Browan Sound Telemetry

- [x] T008 [US2] Write test cases for Browan ingestion in `backend/tests/unit/test_browan_ingest.py`
- [x] T009 [US2] Implement `POST /browan` handler in `backend/sim_server.py`
- [x] T010 [US2] Implement decibel updates mapped to `browan-ingest.json` schema

---

## Phase 4: User Story 3 - Public Telemetry Retrieval

- [x] T011 [US3] Implement `GET /history` public endpoint to serve location tracking sequences
- [x] T012 [US3] Implement `GET /browan` and related stats endpoints for dashboard consumption

---

## Phase 5: Polish & Validation

- [x] T013 Verify Authorization header checks (`tracker_key`) reject unauthorized POST requests
- [x] T014 Run Quickstart scenario validation tests
