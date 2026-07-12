# Data Model: LoRa Telemetry Ingestion

This document details the DynamoDB Single-Table schema used to store telemetry and manage device status for T1000 (tracking) and Browan (sound) LoRa devices.

---

## 1. Single-Table Key Mappings

The DynamoDB table uses a composite primary key system to isolate datasets while maintaining high-performance queries:
- **Partition Key (`event`)**: String representation of the target resource.
- **Sort Key (`type`)**: String representation of the record classifier or timestamp.

| Resource / Type | Partition Key (`event`) | Sort Key (`type`) | Purpose |
| :--- | :--- | :--- | :--- |
| **T1000 Ingest Log** | `device#<device_id>` | `telemetry#<timestamp>` | Historical record of individual T1000 readings. |
| **Browan Ingest Log** | `device#<device_id>` | `telemetry#<timestamp>` | Historical record of individual Browan sound readings. |
| **Device State Singleton** | `device#<device_id>` | `state` | Current state, location history, and last known GPS coordinate. |

---

## 2. Record Schemas

### A. Device State Singleton
* **Partition Key (`event`)**: `device#<device_id>` (e.g., `device#eui-70b3d57ed0051111`)
* **Sort Key (`type`)**: `state`

```json
{
  "event": "device#eui-70b3d57ed0051111",
  "type": "state",
  "device_id": "eui-70b3d57ed0051111",
  "device_type": "T1000" | "Browan",
  "last_updated": "2026-07-10T12:00:00Z",
  "last_known_latitude": 51.5074,
  "last_known_longitude": -0.1278,
  "last_known_timestamp": "2026-07-10T12:00:00Z",
  "location_history": [
    { "lat": 51.5074, "lng": -0.1278, "time": "2026-07-10T12:00:00Z" }
  ]
}
```

#### Validation Rules & Constraints:
- `location_history` MUST contain an array of objects.
- `location_history` MUST be capped at a maximum of exactly 20 elements (Principle IV). When a 21st location is added, the oldest element (index 0) is discarded.

---

### B. T1000 Telemetry Historical Log
* **Partition Key (`event`)**: `device#<device_id>` (e.g., `device#eui-70b3d57ed0051111`)
* **Sort Key (`type`)**: `telemetry#<timestamp>` (e.g., `telemetry#2026-07-10T12:05:00Z`)

```json
{
  "event": "device#eui-70b3d57ed0051111",
  "type": "telemetry#2026-07-10T12:05:00Z",
  "device_id": "eui-70b3d57ed0051111",
  "timestamp": "2026-07-10T12:05:00Z",
  "temperature": 23.4,
  "light": 140,
  "latitude": null,
  "longitude": null,
  "last_known_latitude": 51.5074,
  "last_known_longitude": -0.1278,
  "last_known_timestamp": "2026-07-10T12:00:00Z",
  "staleness_seconds": 300
}
```

#### Validation Rules & Constraints:
- `temperature`: Float (valid range: `-40.0` to `80.0` °C). Anomalous out-of-bounds readings are discarded.
- `light`: Integer (valid range: `0` to `100000` Lux).
- `latitude` / `longitude`: Decimal degrees or `null` if GPS lock is missing.
- `staleness_seconds`: Difference in seconds between `timestamp` and `last_known_timestamp`.

---

### C. Browan Telemetry Historical Log
* **Partition Key (`event`)**: `device#<device_id>` (e.g., `device#eui-70b3d57ed0062222`)
* **Sort Key (`type`)**: `telemetry#<timestamp>` (e.g., `telemetry#2026-07-10T12:05:00Z`)

```json
{
  "event": "device#eui-70b3d57ed0062222",
  "type": "telemetry#2026-07-10T12:05:00Z",
  "device_id": "eui-70b3d57ed0062222",
  "timestamp": "2026-07-10T12:05:00Z",
  "sound_level": 48.5
}
```

#### Validation Rules & Constraints:
- `sound_level`: Float representing instantaneous noise level in decibels (valid range: `0.0` to `150.0` dB).
