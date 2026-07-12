# Data Model: Production Infrastructure Deployment

This document maps the production AWS DynamoDB partition structures, indexing strategies, and throughput configurations provisioned via Terraform.

---

## 1. Production Table Keys & Indexes

In alignment with **Principle IV (Safe and Secure Database Modeling)**, the production database is provisioned as a single table utilizing composite keys with On-Demand (PAY_PER_REQUEST) capacity:

* **Table Name**: `open_emfer_v2_production`
* **Partition Key (`event`)**: String (e.g. `camper#aggregates#ali`, `device#eui-70b3...`)
* **Sort Key (`type`)**: String (e.g. `totals`, `telemetry#2026-07-10T12:00:00Z`)

| Attribute | Type | Role | Description |
| :--- | :--- | :--- | :--- |
| `event` | `S` (String) | Partition Key (HASH) | Isolates resource domains and camper namespaces. |
| `type` | `S` (String) | Sort Key (RANGE) | Maps log entries chronologically or identifies state singletons. |

---

## 2. Secrets Manager Payload Mapping

Private credentials required at runtime are stored in an AWS Secrets Manager secret named `open_emfer_v2_production_vault`:

### JSON Object Keys:
```json
{
  "tracker_key": "super-secret-gateway-authorization-token",
  "monzo_client_id": "oauth-client-id-here",
  "monzo_client_secret": "oauth-client-secret-here"
}
```

#### Runtime Loading:
AWS Lambda functions fetch and parse this JSON payload dynamically during cold starts, avoiding hardcoded keys inside version control (complying with **Principle V**).
