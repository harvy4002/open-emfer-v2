# Quickstart Validation Guide: Open EMF Camper API

This guide describes the runnable end-to-end validation scenarios that verify the core Open EMF Camper API functions correctly.

---

## Prerequisites & Setup

1. **Local Test Environment**: Ensure you have Python 3.12+ installed.
2. **Dependencies**:
   ```bash
   pip install pytest moto boto3
   ```
3. **Configure Environment Variables**: Set the mock authentication key:
   ```bash
   export TRACKER_KEY="super-secret-tracker-key"
   ```

---

## Validation Scenario 1: Log standard drink (POST `/beer`)

Verifies that sending a valid logging request increments the correct aggregate counts.

### Execute Command
```bash
curl -X POST https://api.camper.local/beer \
  -H "Authorization: super-secret-tracker-key" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "Drinks",
    "type": "Lager"
  }'
```

### Expected Outcome
- **Response Code**: `201 Created`
- **Response Body**:
  ```json
  {
    "status": "success",
    "category": "Drinks",
    "name": "Lager",
    "beer": true,
    "reverse": false
  }
  ```

---

## Validation Scenario 2: Reverse standard drink (POST `/beer` with `reverse: true`)

Verifies that logging with `"reverse": true` offsets the historical counts.

### Execute Command
```bash
curl -X POST https://api.camper.local/beer \
  -H "Authorization: super-secret-tracker-key" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "Drinks",
    "type": "Lager",
    "reverse": true
  }'
```

### Expected Outcome
- **Response Code**: `201 Created`
- **Response Body**:
  ```json
  {
    "status": "success",
    "category": "Drinks",
    "name": "Lager",
    "beer": true,
    "reverse": true
  }
  ```

---

## Validation Scenario 3: Retrieve aggregated stats (GET `/beer`)

Verifies public retrieval of current totals.

### Execute Command
```bash
curl -X GET https://api.camper.local/beer?event=drinks
```

### Expected Outcome
- **Response Code**: `200 OK`
- **Response Body**: Matches [beer-get.json](./contracts/beer-get.json) schema:
  ```json
  {
    "status": "success",
    "last_updated": "2026-07-10T12:00:00Z",
    "categories": {
      "Lager": 14,
      "Water": 12
    },
    "total_drinks": 26,
    "beer_drinks": 14
  }
  ```

---

## Validation Scenario 4: Unauthorized Access

Verifies rejection of POST payloads lacking correct auth keys.

### Execute Command
```bash
curl -X POST https://api.camper.local/beer \
  -H "Authorization: invalid-key" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "Drinks",
    "type": "Lager"
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
