# Quickstart Validation Guide: LoRa Telemetry Ingestion

This guide describes the runnable end-to-end validation scenarios that verify the T1000 and Browan LoRa ingestion handlers work as specified.

---

## Prerequisites & Setup

1. **Local Test Environment**: Ensure you have Python 3.12+ installed.
2. **Dependencies**: Install development and testing dependencies:
   ```bash
   pip install pytest moto boto3
   ```
3. **Environment Configuration**: Set a mock secret key for gateway signature validation:
   ```bash
   export TRACKER_KEY="mock-super-secret-key"
   ```

---

## Validation Scenario 1: T1000 Ingestion (Valid GPS Lock)

Verifies that sending a fully formed T1000 payload with valid GPS coordinates results in a successful DB record creation and appends coordinates to the location history array.

### Execute Command (Mock HTTP POST)
Submit a mock payload corresponding to [t1000-ingest.json](./contracts/t1000-ingest.json) using curl:
```bash
curl -X POST https://api.camper.local/telemetry/t1000 \
  -H "Authorization: mock-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "eui-70b3d57ed0051111",
    "timestamp": "2026-07-10T12:00:00Z",
    "temperature": 24.5,
    "light": 150,
    "location": {
      "latitude": 51.5074,
      "longitude": -0.1278
    }
  }'
```

### Expected Outcome
- **Response Code**: `201 Created`
- **Response Body**:
  ```json
  {
    "status": "success",
    "device_id": "eui-70b3d57ed0051111",
    "staleness_seconds": 0
  }
  ```
- **DynamoDB Verification**:
  - A historical log record is created under the Partition Key `device#eui-70b3d57ed0051111` and Sort Key `telemetry#2026-07-10T12:00:00Z`.
  - The `state` singleton record is updated, showing `location_history` with 1 item.

---

## Validation Scenario 2: T1000 Ingestion (Missing GPS Lock / Fallback)

Verifies that sending a T1000 payload with a `null` location gracefully saves ambient temperature and light while retaining the last known location from the `state` singleton and calculating correct coordinate staleness.

### Execute Command (Mock HTTP POST)
Submit a payload with location set to `null` 10 minutes (600 seconds) after Scenario 1:
```bash
curl -X POST https://api.camper.local/telemetry/t1000 \
  -H "Authorization: mock-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "eui-70b3d57ed0051111",
    "timestamp": "2026-07-10T12:10:00Z",
    "temperature": 25.0,
    "light": 145,
    "location": null
  }'
```

### Expected Outcome
- **Response Code**: `201 Created`
- **Response Body**:
  ```json
  {
    "status": "success",
    "device_id": "eui-70b3d57ed0051111",
    "staleness_seconds": 600
  }
  ```
- **DynamoDB Verification**:
  - The historical log `telemetry#2026-07-10T12:10:00Z` shows `latitude: null`, `longitude: null`, `last_known_latitude: 51.5074`, `last_known_longitude: -0.1278`, and `staleness_seconds: 600`.
  - The `state` singleton's coordinate history is unchanged (still 1 item), but the current telemetry metrics are stored.

---

## Validation Scenario 3: Browan Sound Ingestion

Verifies that Browan ambient decibel noise telemetry is successfully ingested and persisted.

### Execute Command (Mock HTTP POST)
Submit a sound telemetry payload matching [browan-ingest.json](./contracts/browan-ingest.json):
```bash
curl -X POST https://api.camper.local/telemetry/browan \
  -H "Authorization: mock-super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "eui-70b3d57ed0062222",
    "timestamp": "2026-07-10T12:05:00Z",
    "sound_level": 45.2
  }'
```

### Expected Outcome
- **Response Code**: `201 Created`
- **Response Body**:
  ```json
  {
    "status": "success",
    "device_id": "eui-70b3d57ed0062222"
  }
  ```
- **DynamoDB Verification**:
  - A sound log is saved under PK `device#eui-70b3d57ed0062222` and SK `telemetry#2026-07-10T12:05:00Z`.

---

## Validation Scenario 4: Authorization Rejection

Verifies that requests with missing or invalid `tracker_key` values are rejected with 401 Unauthorized errors.

### Execute Command (Mock HTTP POST)
```bash
curl -X POST https://api.camper.local/telemetry/browan \
  -H "Authorization: wrong-key" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "eui-70b3d57ed0062222",
    "timestamp": "2026-07-10T12:05:00Z",
    "sound_level": 45.2
  }'
```

### Expected Outcome
- **Response Code**: `401 Unauthorized`
- **Response Body**:
  ```json
  {
    "error": "Unauthorized",
    "message": "Invalid or missing tracker key"
  }
  ```
- **DynamoDB Verification**: No data was written to the table.
