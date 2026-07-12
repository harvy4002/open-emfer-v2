# Technical Research: Multi-User Tracking

This document details the architectural decisions and patterns adopted to support multi-user isolation, real-time combined statistics, and QR-optimized client routing on a serverless stack.

---

## 1. Dual-Write Pre-Aggregation

### Decision
When an authenticated logging event (e.g., drinks, status, toilet visit) is received via `POST /beer`, the backend Lambda will execute a dual-write (via `boto3` TransactWriteItems or consecutive updates):
1. Increment the specific user's aggregate partition (`camper#aggregates#<user_id>`).
2. Increment the global combined aggregate partition (`camper#aggregates#combined`).

### Rationale
- **Low-Latency Reads**: Reading the combined stats dashboard (`?u=combined`) will require a single low-latency DynamoDB `GetItem` call on the `combined` partition, rather than executing expensive `Scan` operations or querying multiple users' individual records on every page load.
- **Serverless Scaling**: Pre-aggregation (calculating totals at write-time) perfectly aligns with Serverless Cost-Optimization limits.

### Alternatives Considered
- **On-the-Fly Aggregation (Read-Time)**: Rejected. Querying all user profiles and summing their numbers during a GET request would drastically increase DynamoDB read capacity units (RCU) and latency, particularly if dozens of users are registered.

---

## 2. Client-Side QR Routing & Binding

### Decision
Rely purely on browser-side `URLSearchParams` to extract the `u` parameter (`?u=ali`) in the frontend static assets. No server-side routing (SSR) or CloudFront Lambda@Edge rewrites will be used.
- If `?u=ali` is present: The JS binds all API fetches and admin POSTs to `{ "user_id": "ali" }`.
- If `?u=` is omitted: The JS defaults to the legacy hardcoded owner profile (`hvy`) to ensure backward compatibility.
- If `?u=combined` is present: The JS loads the `combined` totals and hides the individual tracking/environmental charts.

### Rationale
- **QR Density Optimization**: Keeping the URL extremely compact directly minimizes the physical dot density of the printed QR codes, allowing for instant, sub-second scanning in the field even under poor lighting.
- **Static Hosting Compliance**: Keeps the S3 bucket fully static (Principle VII). S3 does not easily support dynamic pathing (like `/user/ali`) without complex error-document routing hacks.

### Alternatives Considered
- **CloudFront Functions / Lambda@Edge**: Rejected as over-engineered and costly for simple parameter passing.
- **Subdirectories in S3 (`/ali/index.html`)**: Rejected because it would require duplicating the HTML/JS frontend assets for every camper.

---

## 3. Atomic Increment Overwrites (Race Conditions)

### Decision
Utilize DynamoDB `UpdateItem` with an `ADD` or `SET num = if_not_exists(num, 0) + :val` UpdateExpression for all logging endpoints.

### Rationale
- **Concurrency Safety**: Ensures that if two users (or the same user) rapidly double-tap the "Log Lager" button, the requests do not overwrite each other's read-state. The database increments safely at the storage layer.

---

## 4. Mobile-First Event Throttling (Double-Tap Protection)

### Decision
Implement a 500ms `setTimeout` button disable script in `admin.js` immediately upon form submission.

### Rationale
- **Physical Field Conditions**: Users walking outdoors frequently accidentally double-tap screens. Client-side throttling prevents duplicate network POSTs before they hit the API.
