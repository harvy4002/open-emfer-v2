# Implementation Plan: LoRa Telemetry Ingestion

**Branch**: `003-lora-telemetry-ingestion` | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-lora-telemetry-ingestion/spec.md`

**Note**: This plan defines the technical architecture, data modeling, API contracts, and validation steps for the LoRa Ingestion feature, fully aligned with the serverless rules of the Constitution.

## Summary

This feature implements two public-facing API Gateway v2 HTTP ingestion endpoints backed by serverless Python 3.12 AWS Lambda functions. The endpoints ingest pre-decoded, standardized JSON telemetry from a LoRa Network Server (LNS) representing:
1. **T1000 Tracking Devices**: Latitude, longitude (nullable), ambient temperature, and light levels.
2. **Browan Sound Sensors**: Ambient noise level in decibels (dB).

The Lambda functions validate the `tracker_key` authorization token, calculate GPS position staleness if a T1000 GPS lock is missing, maintain a rolling 20-entry location coordinate history array per device, and store the metrics in a single DynamoDB table utilizing a composite-key structure compliant with the Open EMF Camper Constitution.

## Technical Context

**Language/Version**: Python 3.12+ (as mandated by backend Constitution principles)

**Primary Dependencies**: AWS SDK for Python (`boto3`) and the standard Python library (keeping Lambdas extremely lightweight and cold-start optimized).

**Storage**: Amazon DynamoDB (On-Demand capacity) utilizing a single-table composite key design.

**Testing**: `pytest` and `moto` for local mock validation of DynamoDB and AWS services.

**Target Platform**: AWS Lambda with API Gateway v2 HTTP APIs proxy integrations.

**Project Type**: web-service.

**Performance Goals**: Processing and saving ingestion telemetry in < 500ms (P95 latency).

**Constraints**: 
* Telemetry mutative writes strictly authenticated against a secure header-based `tracker_key` token.
* Strict DynamoDB array bounds (maximum of 20 elements) for coordinate tracking history (Principle IV).

**Scale/Scope**: Ingests high-frequency telemetry logs from multiple physical camp devices during active camp operations.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Standard | Status | Verification & Alignment |
| :--- | :--- | :--- |
| **I. Contract-First Development** | ✅ PASS | Interface schema defined in OpenAPI/Contracts first before implementation. |
| **II. Serverless Simplicity** | ✅ PASS | Lightweight Python 3.12 Lambda functions utilizing `boto3` and standard library primitives. |
| **III. Infrastructure-as-Code** | ✅ PASS | Provisioning strictly modeled through Terraform in `tf/`. |
| **IV. Safe Database Keys** | ✅ PASS | Partition Key (`event`) and Sort Key (`type`) are strictly mapped. Rolling GPS array is capped at 20 entries. |
| **V. Zero-Trust Security** | ✅ PASS | Ingestion POSTs authenticated via secure `tracker_key` loaded from secrets or header environment variable. |
| **VI. Automated Testing** | ✅ PASS | Handlers tested locally with `pytest` and full service mockery via `moto`. |
| **VII. S3 & CloudFront static frontend**| ✅ PASS | Ingestion services expose standard JSON API responses queried by static dashboards. |

## Project Structure

### Documentation (this feature)

```text
specs/003-lora-telemetry-ingestion/
├── spec.md              # Feature specification
├── plan.md              # Technical implementation plan
├── research.md          # Technical research and choices
├── data-model.md        # Single-table DynamoDB layout
├── quickstart.md        # Scenario testing and validation guide
└── contracts/           # API JSON schema endpoints
    ├── t1000-ingest.json
    └── browan-ingest.json
```

### Source Code (repository root)

```text
backend/
├── lambdas/
│   ├── t1000_ingest/
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── browan_ingest/
│       ├── handler.py
│       └── requirements.txt
└── tests/
    ├── unit/
    │   ├── test_t1000_ingest.py
    │   └── test_browan_ingest.py
    └── mocks/

tf/
├── main.tf
├── api_gateway.tf
├── lambdas.tf
├── dynamodb.tf
└── variables.tf
```

**Structure Decision**: Codebase structured into lightweight, isolated folders for lambdas (`backend/lambdas/`) to support independent cold-start minimization and simple dependency shipping, while Terraform modules (`tf/`) handle IaC.

## Complexity Tracking

*No Constitution violations detected. All designs strictly comply with Open EMF Camper architectural boundaries.*
