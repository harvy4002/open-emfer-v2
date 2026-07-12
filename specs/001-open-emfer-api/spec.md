# Feature Specification: Open EMF Camper API

**Feature Branch**: `main`

**Created**: 2026-07-04

**Status**: Verified / Documented

**Input**: Reverse engineered from the existing Lambda functions, Terraform API Gateway routes, frontend templates, and test HTTP request files.

---

## Purpose and Overview

The **Open EMF Camper API** is a self-hosted personal tracking API for camping events (specifically tailored to Electromagnetic Field - EMF Camp). It records real-time human activities, tracker statuses, Monzo transaction summaries, environmental conditions from LoRa IoT devices (Sensecap T1000 and Browan Sound sensors), and lecture/workshop learning progress. All of this telemetry is persisted to AWS DynamoDB and integrated directly with a public dashboard for EMF attendees and personal telemetry displays (e.g., Grafana).

---

## User Scenarios & Testing

### User Story 1 - Log Camper Telemetry (Priority: P1)
As a camper/tracker operator, I want to submit real-time telemetry such as drinks consumed, current activity status, toilet visits, session learning state (lectures/workshops), gaming, and tent visits via a simple HTTP API or web-based dashboard so that my personal telemetry is continuously aggregated.

**Why this priority**: Core tracking capability of the app. Without it, there is no data to display on the dashboard.

**Independent Test**: Can be tested by sending a POST request to `/beer` with valid body parameters and authorization key, then verifying that the aggregate count increments in the DynamoDB table.

**Acceptance Scenarios**:
1. **Given** a valid authentication key in the header, **When** I POST to `/beer` with `"event": "Drinks"` and `"type": "Lager"`, **Then** the request is successful, the raw log is written with a UUID, and the aggregate count for Drinks is updated in the table with `"beer": true`.
2. **Given** an invalid or missing authentication key, **When** I POST to `/beer`, **Then** I receive a `401 Unauthorized` response.

---

### User Story 2 - Retrieve Dashboard Statistics (Priority: P1)
As an attendee or dashboard viewer, I want to query the current telemetry totals, active status, environmental parameters, and location history so that I can see the real-time stats of the tracker.

**Why this priority**: Essential for visual outputs and presentation to the public/attendee dashboard.

**Independent Test**: Can be tested by performing GET requests to `/beer?event=drinks`, `/sensecap`, `/browan`, `/history`, and `/monzo`, and verifying the returned JSON payload schema.

**Acceptance Scenarios**:
1. **Given** active telemetry in the system, **When** I GET `/beer?event=status&type=latest`, **Then** I receive a single JSON object with the current status and corresponding image URL (e.g. `harvy_chilling.jpg`).
2. **Given** sensor and location updates, **When** I GET `/history`, **Then** I receive location history (max 20 records) along with lecture and workshop summaries, gaming seconds, and total raw data row count.

---

### User Story 3 - LoRa IoT Device Ingestion (Priority: P2)
As an IoT sensor network (ChirpStack integration), I want to POST binary sensor payloads containing GPS coordinates, temperature, ambient light, noise levels, and battery metrics to a centralized ingest endpoint so that my environmental context is captured in real time.

**Why this priority**: Automates the ambient tracking of the camper (where they are, what the temperature/light/sound level is).

**Independent Test**: Can be tested by sending a POST to `/sensecap` with ChirpStack payload format and verifying that coordinates are translated, cumulative distances/steps are computed using the Haversine formula, and environmental aggregates are updated.

**Acceptance Scenarios**:
1. **Given** a POST request to `/sensecap` with device EUI `2CF7F1C0546002A3`, **When** the payload is processed, **Then** the location history (`Location`/`History`) is updated with computed cumulative distance (km) and steps, and current ambient metrics are saved to `Sensecap`/`Latest`.
2. **Given** a POST request to `/sensecap` with device name `h02`, **When** the payload is processed, **Then** the aggregate Sound table (`Sound`/`Exact`) is updated with noise level, temperature, and battery life.

---

### User Story 4 - Bank Transaction Monitoring (Priority: P3)
As a camper, I want the system to periodically query my bank (Monzo API) in the background to retrieve recent expenditure so that the public dashboard can display my latest camp expenditure.

**Why this priority**: Enhances telemetry with financial context but operates as an asynchronous background sync.

**Independent Test**: Triggering the monzo lambda handler without `httpMethod` in the event triggers the cron mechanism to fetch from Monzo, perform conversion/re-mapping, and store transactions.

**Acceptance Scenarios**:
1. **Given** a cron event trigger, **When** the monzo handler runs, **Then** it authenticates with Monzo using credentials in Secrets Manager, fetches new transactions, adds adjusted amount and description flags, and batch-updates the DynamoDB tables.
2. **Given** an API Gateway GET request to `/monzo`, **When** the endpoint is queried, **Then** the last cached transactions are retrieved from DynamoDB aggregate table and returned as JSON.

---

## Edge Cases

- **Token Reversals**: A user accidentally logs a drink or status and wants to undo it. The system handles this using a `"reverse": true` parameter in the `/beer` POST payload, which subtracts from the aggregate count instead of adding to it.
- **First Location Point**: When location history is completely empty in DynamoDB, the first point must be processed with `0` cumulative distance and `0` steps, preventing division or addition errors with None values.
- **Non-Standard Drink Tracking**: The UI allows custom text inputs for drinks. If the drink is in the pre-defined list of beer types (e.g., `Lager`, `IPA`, `Cider`), the `beer` flag is stored as `true`, while custom drinks store `beer` as `false` but still count toward the total drinks metric.
- **Learning Session Stop without Start**: If a stop event is triggered for a lecture/workshop without a previous start event, the API might return an error or fail to match. The system expects a start event to exist to calculate learning duration, retrieving the `start_timestamp` from the raw table.

---

## Requirements

### Functional Requirements

- **FR-001 (Auth)**: The system MUST validate incoming POST requests to `/beer` against the `TRACKER_KEY` configuration. Unauthenticated requests MUST return a `401 Unauthorized` status.
- **FR-002 (CORS)**: The API Gateway and HTTP resources MUST allow Cross-Origin Requests (CORS) from authorized dashboard domains (e.g., Grafana and S3 Slices).
- **FR-003 (Aggregate Metrics)**: Total drinks query (`GET /beer?event=drinks`) MUST compute and return the combined sum of all drinks and beers as an appended JSON object.
- **FR-004 (Haversine Tracking)**: The LoRa ingest logic MUST calculate the earth distance in kilometers using the Haversine formula and update cumulative steps assuming a mean stride length of 0.63 meters.
- **FR-005 (Location Limit)**: The location history saved in aggregate tables MUST contain a maximum of 20 elements to keep payload sizes lightweight and token-efficient.
- **FR-006 (Transaction Parsing)**: For Monzo transactions, positive credit card transactions (where counterparty is not null) MUST be converted into formatted strings labeled `(CREDIT)` and amounts divided/offset.
- **FR-007 (Status Mapping)**: The API MUST dynamically resolve status types to pre-configured public image URLs to show visual mood boards.
- **FR-008 (Reset Capabilities)**: Triggering a reset payload (`event="Reset"`, `type="ResetDay"`) MUST scan the aggregates database and zero out counts across all tracked categories.
