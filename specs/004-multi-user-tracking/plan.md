# Implementation Plan: Multi-User Tracking

**Branch**: `004-multi-user-tracking` | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-multi-user-tracking/spec.md`

**Note**: This plan establishes the architectural patterns, database schemas, and frontend caching updates necessary to support multi-user isolated tracking and combined public aggregations while maintaining serverless constraints.

## Summary

This feature extends the core API and Public Dashboard to support multiple campers concurrently. The backend API (Python 3.12 Lambdas) will accept a `user_id` parameter to isolate logs and aggregates, while dual-writing global sums to a `combined` aggregate DynamoDB partition. The static frontend will extract a compact URL query parameter `u` (e.g., `?u=ali`) optimized for sub-second physical QR-code scans, bind it to LocalStorage, and use it to filter API requests for both the public viewer and the authenticated admin logger.

## Technical Context

**Language/Version**: Python 3.12+, Vanilla HTML/JS/CSS.

**Primary Dependencies**: AWS SDK for Python (`boto3`), Bulma CSS, Chart.js.

**Storage**: Amazon DynamoDB (Single-Table composite key), Browser `localStorage`.

**Testing**: `pytest`, `moto`, browser DevTools responsive testing.

**Target Platform**: AWS Lambda with API Gateway v2, Amazon S3 Static Sites via CloudFront.

**Project Type**: web-service + web-application.

**Performance Goals**: < 500ms P95 API latency for dual-write updates, < 1 second QR-code scan resolution on mobile.

**Constraints**:
* Maintain strict array bounds for coordinate history (max 20 entries) per user profile (Principle IV).
* Frontend layout must be mobile-first with 48px touch targets and vertical stacking (to 320px).
* Extremely compact frontend URL keys (3-4 characters) for optimal QR density.

**Scale/Scope**: Supports the active tracking of multiple individual campers plus a pre-aggregated combined view.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Standard | Status | Verification & Alignment |
| :--- | :--- | :--- |
| **I. Contract-First Development** | ✅ PASS | Data payload schema expanded to include `user_id` identifier. |
| **II. Serverless Simplicity** | ✅ PASS | Pure Python Lambda logic and native JS DOM manipulation without frameworks. |
| **III. Infrastructure-as-Code** | ✅ PASS | All backend infrastructure and CDN distributions provisioned via Terraform. |
| **IV. Safe Database Keys** | ✅ PASS | Single-table partitioned per camper (`camper#aggregates#<user_id>`). History arrays remain strictly capped per user. |
| **V. Zero-Trust Security** | ✅ PASS | Mutative queries to specific camper profiles retain the global `tracker_key` authorization check. |
| **VI. Automated Testing** | ✅ PASS | DynamoDB mock tests verify correct partition isolation and dual-write mechanics. |
| **VII. S3 & CloudFront static frontend**| ✅ PASS | Client-side parameter parsing (`?u=ali`) avoids requiring SSR routing containers. |

## Project Structure

### Documentation (this feature)

```text
specs/004-multi-user-tracking/
├── spec.md              # Feature specification
├── plan.md              # Technical implementation plan
├── research.md          # Technical research and choices
├── data-model.md        # Updated DynamoDB mappings & State layouts
├── quickstart.md        # Scenario testing and validation guide
└── checklists/
    └── requirements.md  # General spec quality checklist
```

### Source Code (repository root)

```text
backend/
├── lambdas/
│   ├── beer_handler/
│   │   └── handler.py   # Updated to handle `user_id` and dual-writes
│   ├── sensecap_ingest/
│   │   └── handler.py   # Updated per-user isolated device state tracking
│   └── browan_ingest/
│       └── handler.py   # Updated to map sound levels to specific user
└── tests/
    └── unit/
        └── [updated test cases for isolated user_id logic]

web/
├── js/
│   ├── app.js           # Updated to parse ?u= parameter and filter fetches
│   └── admin.js         # Updated to submit ?u= parameter on POSTs
├── index.html           # Responsive layout structural updates
└── admin.html           # Responsive layout + profile switcher

tf/
└── [no net-new infrastructure files, existing tables & buckets used]
```

**Structure Decision**: Codebase relies entirely on extending the existing single-project structure under `backend/`, `web/`, and `tf/` without introducing new sub-systems or container layers.

## Complexity Tracking

*No Constitution violations detected. All multi-user partitions and CDN routing patterns conform fully to the established serverless rules.*
