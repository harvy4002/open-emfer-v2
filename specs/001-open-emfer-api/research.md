# Technical Research: Open EMF Camper API

This document details the critical technical decisions, mathematical models, and integration patterns established for the core Open EMF Camper API handlers.

---

## 1. Haversine Distance Tracking & Stride Estimation

### Decision
Implement the Haversine formula inside the LoRa GPS ingestion handlers to calculate the absolute geographic distance (in kilometers) between consecutive GPS updates. The calculated distance increments are converted into "camper steps" based on a mean stride length of **0.63 meters** (0.00063 km).

$$d = 2 R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1) \cos(\phi_2) \sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
* Where $R = 6371$ km (Earth's radius), $\phi$ is latitude in radians, and $\lambda$ is longitude in radians.

### Rationale
- **Stateless Integration (Principle II)**: Calculating distance incremental differences using the previous location cached in the `state` singleton prevents having to fetch all historical rows from DynamoDB on every write.
- **Accurate Steps Proxy**: For physical IoT track tags that lack accelerometer-based pedometers (like simple LoRa trackers), converting computed Haversine travel distance directly to steps via stride length represents a highly reliable aggregate proxy.

### Alternatives Considered
- **Flat-Plane Coordinate Approximation (Euclidean)**: Rejected because flat approximation introduces high inaccuracies over larger camping ground boundaries.

---

## 2. Ingest Log Reversals (`"reverse": true`)

### Decision
Expose a `"reverse": true` parameter in the `/beer` (Drinks and Activities Logging) request schema. When a request with this parameter is received, instead of adding or incrementing counts, the handler performs an offset accounting operation to deduct/subtract from the cached aggregates table.

### Rationale
- **Self-Healing Usability**: Campers logging items in real-time from a mobile UI occasionally double-tap buttons or make mistakes. Allowing a logical "undo" action (reversing the transaction count) via standard HTTP requests avoids database drift without needing manual DB operations or SSH access.

---

## 3. Bank Transaction Re-mapping Format

### Decision
Index and cache bank transactions asynchronously using a serverless cron job. Positive credit transactions (credits, deposits) are identified (where counterparty metadata is not null) and re-mapped by:
1. Converting currency totals in cents/pence to floating decimal pounds (divided by 100).
2. Appending the formatted prefix `(CREDIT)` to the transaction description.
3. Formulating an expense balance metric.

### Rationale
- **Dashboard Consistency**: Keeps formatting uniform and easily readable on a low-bandwidth mobile UI without requiring the client browser to parse currencies and format strings.

---

## 4. API Gateway CORS Policy & Zero-Trust

### Decision
Configure explicit Cross-Origin Resource Sharing (CORS) headers in API Gateway:
- `Access-Control-Allow-Origin`: Explicitly matched allowed domains (S3 dashboards and Grafana).
- `Access-Control-Allow-Headers`: `Content-Type`, `Authorization`.
- `Access-Control-Allow-Methods`: `GET`, `POST`, `OPTIONS`.

### Rationale
- **Principle VII Frontend Decoupling**: Since both dashboards run as static S3/CloudFront pages in client browsers, secure CORS configuration is required to allow browser fetches to communicate securely with API endpoints without exposing vulnerabilities.
