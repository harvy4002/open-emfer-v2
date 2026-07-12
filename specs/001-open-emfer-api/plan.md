# Implementation Plan: Open EMF Camper API

**Branch**: `main` | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-open-emfer-api/spec.md`

**Note**: This plan establishes the primary technical architecture, database layouts, and API specifications for the core Open EMF Camper API system, ensuring 100% compliance with the project's serverless Constitution.

## Summary

The Open EMF Camper API is a lightweight serverless backend built with Python 3.12 Lambdas and Amazon DynamoDB, exposed via AWS API Gateway v2. It provides ingestion, storage, and retrieval pipelines for personal telemetry (beers/drinks logging, status changes, manual triggers), LoRa IoT environmental telemetry (T1000 GPS coordinates, Browan ambient sound sensors), and asynchronous Monzo Bank transaction indexing.

## Technical Context

**Language/Version**: Python 3.12+ (as mandated by backend Constitution principles)

**Primary Dependencies**: AWS SDK for Python (`boto3`) and Python standard library primitives (minimizing bundle sizes to optimize Lambda cold starts).

**Storage**: Amazon DynamoDB (On-Demand capacity) utilizing a single-table composite key design.

**Testing**: `pytest` and `moto` for local mock validation of AWS services.

**Target Platform**: AWS Lambda with API Gateway v2 HTTP APIs proxy integrations.

**Project Type**: web-service.

**Performance Goals**: Processing and saving ingestion telemetry in < 500ms (P95 latency).

**Constraints**: 
* Telemetry mutative writes strictly authenticated against a secure header-based `tracker_key` token.
* Strict DynamoDB array bounds (maximum of 20 elements) for location history to keep payload sizes minimal and cost-efficient.
* Zero hardcoded secrets; bank and tracker credentials must load dynamically from AWS Secrets Manager.

**Scale/Scope**: Unified API endpoints representing campers' daily logs, bank accounts, and active sensor updates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Standard | Status | Verification & Alignment |
| :--- | :--- | :--- |
| **I. Contract-First Development** | ✅ PASS | Interface schema defined in OpenAPI/Contracts first before implementation. |
| **II. Serverless Simplicity** | ✅ PASS | Lightweight Python 3.12 Lambda functions utilizing `boto3` and standard library primitives. |
| **III. Infrastructure-as-Code** | ✅ PASS | Provisioning strictly modeled through Terraform in `tf/`. |
| **IV. Safe Database Keys** | ✅ PASS | Partition Key (`event`) and Sort Key (`type`) are strictly mapped. Rolling coordinate array is capped at 20 entries. |
| **V. Zero-Trust Security** | ✅ PASS | Ingestion POSTs authenticated via secure `tracker_key`. Monzo credentials stored in AWS Secrets Manager. |
| **VI. Automated Testing** | ✅ PASS | Handlers tested locally with `pytest` and full service mockery via `moto`. |
| **VII. S3 & CloudFront static frontend**| ✅ PASS | Backend endpoints expose standard JSON responses consumed directly by S3/CloudFront hosted static dashboards. |

## Project Structure

### Documentation (this feature)

```text
specs/001-open-emfer-api/
├── spec.md              # Feature specification
├── plan.md              # Technical implementation plan
├── research.md          # Technical research and choices
├── data-model.md        # Single-table DynamoDB layout
├── quickstart.md        # Scenario testing and validation guide
└── contracts/           # API JSON schema endpoints
    ├── beer-post.json
    ├── beer-get.json
    ├── sensecap-post.json
    ├── history-get.json
    └── monzo-get.json
```

### Source Code (repository root)

```text
backend/
├── lambdas/
│   ├── beer_handler/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── sensecap_ingest/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── browan_ingest/
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── monzo_sync/
│       ├── handler.py
│       └── requirements.txt
└── tests/
    ├── unit/
    │   ├── test_beer_handler.py
    │   ├── test_sensecap_ingest.py
    │   └── test_browan_ingest.py
    │   └── test_monzo_sync.py
    └── mocks/

tf/
├── main.tf
├── api_gateway.tf
├── lambdas.tf
├── dynamodb.tf
└── secrets.tf
```

**Structure Decision**: Codebase structured into lightweight, isolated folders for lambdas (`backend/lambdas/`) to support independent cold-start minimization and simple dependency shipping, while Terraform modules (`tf/`) handle IaC.

## Complexity Tracking

*No Constitution violations detected. All designs strictly comply with Open EMF Camper architectural boundaries.*
