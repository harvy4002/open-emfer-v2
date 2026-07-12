# Feature Specification: LoRa Telemetry Ingestion

**Feature Branch**: `003-lora-telemetry-ingestion`

**Created**: 2026-07-10

**Status**: Ready

**Input**: User description: "This application is also recieving data from a T1000 devices which sends data over LoRa, this data includes location, temperature and light. It also recieves data from browan which measures sound. These use endpoints in this app which are sent data from a LoRa gateway. This should be considered in the design"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ingest and Store T1000 LoRa Telemetry (Priority: P1)

As a camp data collector, I want the backend to ingest T1000 sensor telemetry (latitude, longitude, temperature, and light level) posted from the LoRa gateway/LNS, so that it is saved securely and made available for public tracking.

**Why this priority**: Core telemetry data from physical camp tracking trackers must be captured to populate the public dashboard.

**Independent Test**: Send an authorized POST request containing T1000 telemetry metrics to the T1000 ingestion endpoint and verify that a `201 Created` status is returned and the data is recorded in DynamoDB under the appropriate device key.

**Acceptance Scenarios**:

1. **Given** the ingestion endpoint is online and authorized, **When** a valid T1000 payload containing location, temperature, and light metrics is POSTed, **Then** the application stores the metrics in DynamoDB with the correct device ID and timestamp.
2. **Given** an incoming T1000 payload with a valid `tracker_key`, **When** the payload has no GPS lock (invalid location), **Then** the system gracefully stores the temperature and light levels, retains the last known valid location in the database, and exposes the staleness of that location (elapsed time since last valid GPS lock).

---

### User Story 2 - Ingest and Store Browan Sound Telemetry (Priority: P1)

As a camp data collector, I want the backend to ingest Browan sound sensor telemetry (ambient noise level) posted from the LoRa gateway, so that the historical sound levels can be stored and monitored.

**Why this priority**: Sound level monitoring is a core ambient metric that must be collected to populate the camp dashboard.

**Independent Test**: Send an authorized POST request containing Browan sound level telemetry to the Browan ingestion endpoint and verify that a `201 Created` status is returned and the record is saved in DynamoDB.

**Acceptance Scenarios**:

1. **Given** the Browan ingestion endpoint is online and authorized, **When** a valid sound reading is POSTed, **Then** the application records the sound level in DynamoDB under the device's key and a timestamp.

---

### User Story 3 - Public Telemetry Retrieval (Priority: P2)

As a dashboard developer, I want to retrieve the latest LoRa sensor readings via public GET endpoints so that they can be displayed on the public dashboard.

**Why this priority**: Standard retrieval capability to enable visual chart rendering on the Grafana-style static dashboard.

**Independent Test**: Send a GET request to public telemetry endpoints (e.g. `/browan`, etc.) and confirm it returns the most recent metrics in a clean JSON format without requiring authentication.

**Acceptance Scenarios**:

1. **Given** telemetry records exist in DynamoDB, **When** a public GET request is received, **Then** the application returns a clean JSON list of the latest telemetry readings with a `200 OK` status and no keys are exposed.

---

### Edge Cases

- **Anomalous Values**: Telemetry with physically impossible data values (e.g., temperatures below absolute zero, light levels below 0 lux, sound levels below 0 dB) must be discarded or clamped to reasonable bounds.
- **Unauthorized Gateway**: If a POST request contains an invalid, missing, or expired `tracker_key` header, the system must reject the write with a `401 Unauthorized` response to prevent spamming.
- **Duplicate Payload IDs**: If a payload is re-transmitted by the LoRa gateway with the same unique transaction or message counter ID, the system should de-duplicate it to avoid recording duplicate metrics.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (T1000 Ingestion)**: The system MUST expose an HTTP POST endpoint to ingest telemetry data (latitude, longitude, temperature, and light level) from T1000 tracking devices.
- **FR-002 (Browan Ingestion)**: The system MUST expose an HTTP POST endpoint to ingest telemetry data (ambient noise level) from Browan sound sensors.
- **FR-003 (Gateway Authentication)**: Ingestion endpoints MUST strictly authenticate incoming LoRa gateway POST requests using a secure authorization header matching the configured `tracker_key` as mandated by Principle V and VII of the Constitution.
- **FR-004 (DynamoDB Storage)**: The system MUST store ingested telemetry in DynamoDB using the standard composite key design (`event` as Partition Key, `type` as Sort Key) in compliance with Principle IV of the Constitution.
- **FR-005 (Coordinate History Sizing)**: The stored coordinate history for any T1000 device MUST maintain a maximum history length of exactly 20 coordinate entries to optimize DynamoDB storage as mandated by Principle IV of the Constitution.
- **FR-006 (Payload Format)**: Ingestion endpoints MUST accept pre-decoded telemetry payloads in standardized JSON formats sent directly from the LoRa Network Server (LNS).
- **FR-007 (GPS Lock Fallback)**: When a T1000 payload is received with a missing or invalid GPS lock, the system MUST gracefully store the available temperature and light metrics with null current coordinates, while retaining the last known valid GPS coordinate in the database and calculating its staleness (time elapsed since the last valid GPS lock) for dashboard display.

### Key Entities *(include if feature involves data)*

- **T1000Telemetry**: Represents a telemetry record from a T1000 tracking device. Key attributes: device ID, timestamp, temperature, light, latitude (nullable), longitude (nullable), last_known_latitude, last_known_longitude, last_known_timestamp, and staleness_seconds.
- **BrowanTelemetry**: Represents a telemetry record from a Browan sound monitoring device. Key attributes: device ID, timestamp, sound level (dB).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of telemetry payloads successfully authenticated with a valid `tracker_key` are processed and stored in DynamoDB in under 500ms.
- **SC-002**: 100% of unauthorized ingestion attempts are rejected with a 401 Unauthorized response.
- **SC-003**: The stored telemetry data is retrievable via public GET endpoints without exposure of keys or secrets.
- **SC-004**: The system enforces DynamoDB array bounds, limiting GPS location histories to exactly 20 coordinates, preventing unchecked data growth.

## Assumptions

- **Assumption 1**: The LoRa gateway or LNS is capable of adding standard Authorization headers with the `tracker_key` to HTTP POST requests.
- **Assumption 2**: Device identification is passed as a unique hardware EUI (DevEUI) in the POST request body or URL.
- **Assumption 3**: Instantaneous decibel (dB) is used as the standard unit for Browan sound telemetry.
- **Assumption 4**: Ingestion endpoints are served by serverless AWS Lambdas behind HTTP API Gateways, ensuring zero idle cost as required by the Constitution.
