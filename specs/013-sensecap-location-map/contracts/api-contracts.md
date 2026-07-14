# API Contracts: Sensecap Location Map Integration

This document outlines the API request and response formats utilized by the dashboard map to ingest and fetch coordinate details.

## 1. POST `/sensecap`
Ingests location and environmental telemetry from the ChirpStack Chirp webhook representing the Sensecap T1000 LoRa Tracker.

- **Method**: `POST`
- **Path**: `/sensecap`
- **Headers**:
  - `Content-Type`: `application/json`
  - `tracker_key`: `<secure_authentication_token>` (Compliance with Principle V)

### Request Payload Schema
```json
{
  "device_id": "device#eui-70b3d57ed0051111#hvy",
  "timestamp": "2026-07-14T15:30:00Z",
  "latitude": 52.041118,
  "longitude": -2.377757,
  "temperature": 22.5,
  "light": 150
}
```

### Response Payload (201 Created)
```json
{
  "status": "success",
  "message": "Telemetry appended successfully",
  "cumulative_distance_km": 4.25,
  "cumulative_steps": 6746
}
```

---

## 2. GET `/history`
Retrieves aggregated historical tracking logs for the selected user, including the coordinate location list used to plot the interactive map.

- **Method**: `GET`
- **Path**: `/history`
- **Query Parameters**:
  - `user_id` (string, optional, defaults to `hvy`): ID of the camper to load history for.

### Response Payload (200 OK)
```json
{
  "status": "success",
  "user_id": "hvy",
  "cumulative_distance_km": 4.25,
  "cumulative_steps": 6746,
  "location_history": [
    {
      "lat": 52.041118,
      "lng": -2.377757,
      "time": "2026-07-14T13:30:00Z"
    },
    {
      "lat": 52.041520,
      "lng": -2.378100,
      "time": "2026-07-14T14:30:00Z"
    },
    {
      "lat": 52.042100,
      "lng": -2.378900,
      "time": "2026-07-14T15:30:00Z"
    }
  ]
}
```
