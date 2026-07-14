# Data Model: Sensecap Location Map Integration

This document defines the data structures and representation formats used for capturing, persisting, and mapping Sensecap location telemetry.

## 1. Entities

### Entity: `LocationPoint`
Represents an individual physical geographic coordinate check-in captured from the Sensecap T1000 LoRa tracker.

#### Fields
- `lat` (float, mandatory): Latitude in decimal degrees (WGS 84). Must be within valid geographical bounds [-90.0, 90.0].
- `lng` (float, mandatory): Longitude in decimal degrees (WGS 84). Must be within valid geographical bounds [-180.0, 180.0].
- `time` (string, mandatory): ISO 8601 formatted UTC timestamp (e.g., `2026-07-14T15:30:00Z`).

#### Validation Rules
- Latitudes must be between `52.0300` and `52.0550` for the EMF Camp Eastnor Castle bounding area to be considered a local camp point, although any valid global coordinate is accepted.
- Timestamps must be valid ISO 8601 format.

---

### Entity: `LocationHistoryState`
The aggregated device state stored in AWS DynamoDB under a participant's device state partition.

#### Key Schema (DynamoDB Composite Key Model)
- **Partition Key (`PK`)**: `event` value (e.g., `device#eui-70b3d57ed0051111#hvy`)
- **Sort Key (`SK`)**: `state` value

#### Fields
- `last_known_latitude` (float): The most recent latitude reported.
- `last_known_longitude` (float): The most recent longitude reported.
- `last_known_timestamp` (string): The timestamp of the most recent coordinate.
- `cumulative_distance_km` (float): Total physical distance walked in kilometers, computed sequentially via the Haversine formula.
- `cumulative_steps` (integer): Aggregated step count, mapped using a stride length proxy (1 step $\approx$ 0.00063 km).
- `location_history` (list of `LocationPoint` objects): A chronologically ordered array of the last 20 coordinates.

#### Sizing & Boundary Constraints (Compliance with Principle IV)
- The `location_history` array MUST be capped at a **maximum of 20 elements** to optimize DynamoDB item size, reduce read/write costs, and maintain fast payload delivery over low-speed mobile camper networks.
- Oldest entries are popped (`pop(0)`) sequentially when the array length exceeds 20.

---

## 2. Relationships

```text
+-----------------------+              +---------------------+
| LocationHistoryState  | 1       0..20|    LocationPoint    |
| (DynamoDB state key)  |------------->|  (History Array)    |
+-----------------------+              +---------------------+
           |
           | 1
           v
+-----------------------+
|  Participant Profile  |
|   (e.g., user_id)     |
+-----------------------+
```

- Each **Participant** is mapped to a unique **LocationHistoryState** record using their `user_id`.
- A **LocationHistoryState** contains an ordered sequence of 0 to 20 **LocationPoint** entities.
