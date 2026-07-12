# Tasks: Production Infrastructure Deployment

**Input**: Design documents from `specs/006-production-infrastructure/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Scenario testing is handled via `terraform plan` dry-runs and SSL browser query verifications as defined in `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Codebase structured as a decoupled Python/Terraform project under `backend/`, `web/`, and `tf/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize the Terraform files structure under the `tf/` directory including `tf/main.tf` and `tf/variables.tf`
- [x] T002 Configure the AWS providers and the ACM alias provider for `us-east-1` in `tf/main.tf`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Provision the single Amazon DynamoDB composite key table in `tf/dynamodb.tf`
- [x] T004 [P] Provision the secure AWS Secrets Manager secrets and parameter schemas in `tf/secrets.tf`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Live Public Dashboard Access (Priority: P1) 🎯 MVP

**Goal**: Amazon S3 bucket and CloudFront distribution serving static dashboard files globally over HTTPS.

**Independent Test**: Navigate to `https://emf.harvinderatwal.com` and verify that dashboards render over HTTPS.

### Implementation for User Story 1

- [x] T005 [US1] Create ACM SSL certificate for `emf.harvinderatwal.com` in `tf/main.tf` using the `us-east-1` alias provider
- [x] T006 [US1] Provision S3 static website hosting bucket and attach IAM policy in `tf/s3_cloudfront.tf`
- [x] T007 [US1] Provision CloudFront distribution mapping to S3 and caching policies in `tf/s3_cloudfront.tf`
- [x] T008 [US1] Output the DNS ACM validation records and CloudFront domains in `tf/outputs.tf`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Live Telemetry Ingestion (Priority: P1)

**Goal**: API Gateway v2 routing HTTP POSTs and GETs to secure Lambda handlers and DynamoDB.

**Independent Test**: Submit a live drink log from `/admin.html` and confirm S3 webpage triggers a fetch to the CloudFront API domain.

### Implementation for User Story 2

- [x] T009 [US2] Package Python handlers in zip archives using Terraform `archive_file` in `tf/lambda.tf`
- [x] T010 [P] [US2] Provision AWS Lambda functions with IAM execution policies in `tf/lambda.tf`
- [x] T011 [US2] Provision AWS API Gateway v2 HTTP API with proxy routes in `tf/api_gateway.tf`
- [x] T012 [P] [US2] Configure CORS Allowed Origins mapping the production domain in `tf/api_gateway.tf`
- [x] T013 [US2] Update frontend JavaScript API endpoint dynamic binding inside `web/js/app.js` and `web/js/admin.js`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Infrastructure Provisioning and Teardown (Priority: P2)

**Goal**: Unified, zero-manual-effort automated deploys and teardowns.

**Independent Test**: Run `terraform plan` and confirm a clean, complete, conflict-free provisioning roadmap.

### Implementation for User Story 3

- [x] T014 [US3] Write documentation detailing manual Cloudflare CNAME mapping values in `specs/006-production-infrastructure/quickstart.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Code formatting and final validation

- [x] T015 Run `terraform validate` inside `tf/` to verify provider integrations
- [x] T016 [P] Run `ruff check` on Lambda python handlers in `backend/` to ensure PEP 8 compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

---

## Parallel Example: User Story 1

```bash
# Initialize file skeletons simultaneously:
# T004 [P] and T010 [P] can run concurrently
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently
4. Add User Story 3 → Test independently
