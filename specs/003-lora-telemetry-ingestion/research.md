# Technical Research: LoRa Telemetry Ingestion

This document details the core architectural decisions, payload protocols, and database modeling patterns chosen for the T1000 and Browan LoRa telemetry ingestion pipelines.

---

## 1. LoRa Network Server (LNS) Payload Structure

### Decision
Standardize on standard pre-decoded JSON payloads sent from the LoRa Network Server (LNS) utilizing ChirpStack or The Things Network (TTN) HTTP integrations. The backend API Gateway/Lambda functions will not perform raw binary decoding; instead, payload parsers configured on the LNS will translate raw sensor uplinks into structured JSON.

### Rationale
- **Serverless Simplicity (Principle II)**: Shifting binary decoding to the LNS eliminates the need to compile, package, and update low-level codec decoders inside serverless Lambda functions.
- **Dependency Reduction**: Avoids importing complex or heavy node/python parser scripts in Lambda runtimes, optimizing handler sizes and cold start performance.
- **Clean Interface Boundary**: Standardizes on uniform HTTP JSON integrations, allowing easier integration of other gateway vendors in the future.

### Alternatives Considered
- **Raw Hex Parsing in Lambda**: Rejected because it requires the Lambda handlers to maintain complex bitmasking and codec structures for multiple separate hardware devices (T1000 and Browan), leading to high maintenance and deployment overhead.

---

## 2. DynamoDB Single-Table State and History Modeling

### Decision
Model the sensor telemetry and device state tracking in a single Amazon DynamoDB table using composite-key structures:
* **Partition Key (`event`)**: `device#<device_id>`
* **Sort Key (`type`)**: `telemetry#<timestamp>` for historical entries, and `state` for the device's singleton state.

To calculate GPS coordinate staleness and enforce the strict 20-entry coordinate history limit (Principle IV):
1. **Device State Singleton (`device#<device_id>` / `state`)**:
   Stores the device status, rolling array of the last 20 coordinates (`[{ "lat": x, "lng": y, "time": t }]`), and `last_known_location` details:
   ```json
   {
     "event": "device#eui-70b3d57ed005xxxx",
     "type": "state",
     "last_known_latitude": 51.5074,
     "last_known_longitude": -0.1278,
     "last_known_timestamp": "2026-07-10T12:00:00Z",
     "location_history": [
       { "lat": 51.5074, "lng": -0.1278, "time": "2026-07-10T12:00:00Z" }
     ]
   }
   ```
2. **On Ingestion**:
   - The Lambda handler reads the `state` record first.
   - If GPS coordinates are present in the new LNS payload:
     - Update `last_known_latitude`, `last_known_longitude`, and `last_known_timestamp`.
     - Append the new entry to `location_history`.
     - Slice the `location_history` array to retain only the most recent 20 elements.
     - Calculate `staleness_seconds = 0`.
   - If GPS coordinates are missing/null in the new payload:
     - Keep existing `last_known_location` properties unchanged from the `state` record.
     - Calculate `staleness_seconds = current_timestamp - last_known_timestamp`.
   - Write the telemetry log entry (`telemetry#<timestamp>`) and update the `state` singleton.

### Rationale
- **Strict Compliance with Principle IV**: Explicitly caps the array size of coordinate histories to exactly 20 items, avoiding unbounded attribute growth.
- **Stateless Query Optimization**: Storing `last_known_location` and calculated `staleness_seconds` directly with each telemetry record allows dashboards to fetch the latest status in a single GET query without searching through historical tables.
- **Serverless Scaling**: Single-table lookup of the `state` singleton is extremely fast, predictable, and cost-efficient.

### Alternatives Considered
- **No State Record (Dynamic Lookups)**: Querying the DB backwards chronologically to find the last known GPS coordinate. Rejected because it requires expensive, multi-record Scan or Query operations on every ingestion event, which violates our low-latency performance goal and increases DynamoDB read costs under load.

---

## 3. Ingestion Authentication Pattern

### Decision
Standardize on HTTP header token authentication. The LNS HTTP webhook or LoRa Gateway must provide an `Authorization` header with a static secret token matching the application's configured `tracker_key`.

### Rationale
- **Zero-Trust Security (Principle V)**: Ensures only authenticated gateways can POST telemetry, protecting the database from write spam.
- **Sourcing Ease**: Modern LoRa Network Servers natively support custom headers or Authorization tokens for HTTP Webhooks.

### Alternatives Considered
- **Signature Verification / HMAC**: Rejected as too complex for LNS gateways, which often do not support custom cryptography algorithms without expensive enterprise layers.
- **No Authentication**: Strictly prohibited by the Security and Zero-Trust principles of the Open EMF Camper Constitution.
