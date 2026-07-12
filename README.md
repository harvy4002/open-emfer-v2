# Open EMF Camper Dashboard and Telemetry API (V2)

A cost-optimized, highly responsive, serverless ecosystem designed for EMF Camp operations. This project houses the complete specifications, technical designs, database layouts, and development checklists to support real-time activity tracking, environmental telemetry, and bank integrations.

---

## 🏗️ Architecture Overview

The system is engineered for near-zero running cost and high performance under limited mobile network conditions:

* **Backend Services**: Lightweight, single-responsibility **Python 3.12 AWS Lambda** functions served via **API Gateway v2 HTTP APIs**, storing all data in a single Amazon DynamoDB table using composite-key partition structures.
* **Frontend Websites**: Highly responsive, mobile-first **Vanilla HTML5/CSS3/ES6+** static websites hosted in **Amazon S3** buckets and distributed globally via **AWS CloudFront CDN** with short edge caching.
* **IoT & Telemetry**: Native parsing and math models for Haversine distance tracking and stride estimations from LoRa GPS tracking trackers (Sensecap T1000) and ambient sound decibel sensors (Browan).

---

## 📂 Feature Specifications

This workspace contains complete specification and implementation designs for each of the core ecosystem capabilities:

1. **[001-open-emfer-api](./specs/001-open-emfer-api/)**: Core serverless backend API endpoints (`/beer` logging, raw log offsets, Monzo Sync triggers, and `/history`).
2. **[002-public-dashboard](./specs/002-public-dashboard/)**: Responsive, dark-theme Grafana-style visual dashboard grids and participant admin portals.
3. **[003-lora-telemetry-ingestion](./specs/003-lora-telemetry-ingestion/)**: LoRa gateway integrations, coordinate history capping, and missing GPS lock staleness resolvers.
4. **[004-multi-user-tracking](./specs/004-multi-user-tracking/)**: Multi-user query params (`?u=ali`), pre-aggregation dual-writes, responsive column stackings, and physical QR-code optimized short URLs for field scans.

---

## 🧪 Local Validation Guide

### Running the Frontend Locally
Spin up a simple Python static file server inside the assets folder:
```bash
python3 -m http.server -d web 8080
```
Navigate your browser to `http://localhost:8080/index.html` to run local tests.

### Running Backend Unit Tests
Install dependencies and trigger the test suite:
```bash
pip install pytest moto boto3
pytest backend/tests/
```
All AWS services (DynamoDB, Secrets Manager) are mock-simulated offline during testing.
