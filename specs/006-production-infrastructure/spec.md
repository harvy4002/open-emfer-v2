# Feature Specification: Production Infrastructure Deployment

**Feature Branch**: `006-production-infrastructure`

**Created**: 2026-07-10

**Status**: Draft

**Input**: User description: "ok I now want to put this in production as a thin slice and to start user testing. Can speckit do this? yes"

---

## Purpose and Overview

The **Production Infrastructure Deployment** feature transitions the Open EMF Camper application from a local developer simulation to a live, internet-accessible environment suitable for actual user testing in the field. 

It accomplishes this by provisioning the entire required AWS infrastructure (S3, CloudFront, API Gateway, AWS Lambda, DynamoDB, Secrets Manager) using Terraform (Infrastructure-as-Code). This ensures a secure, highly-available, and cost-optimized serverless environment that complies fully with the Open EMF Camper Constitution.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live Public Dashboard Access (Priority: P1)

As a camp visitor in the field, I want to scan a QR code and instantly load the live public telemetry dashboard (`https://emf.harvinderatwal.com/?u=ali`) on my mobile device, so that I can view real-time camper statistics and charts over a cellular connection.

**Why this priority**: Core deliverable. User testing cannot begin until the frontend is securely hosted and publicly resolvable.

**Independent Test**: Navigate to `https://emf.harvinderatwal.com/?u=ali` on a mobile browser and verify that the HTML, CSS, and JS assets load correctly with an active HTTPS certificate.

**Acceptance Scenarios**:

1. **Given** the frontend assets are deployed to Amazon S3, **When** a user navigates to the domain, **Then** AWS CloudFront serves the cached assets over HTTPS with a latency of less than 2 seconds.

---

### User Story 2 - Live Telemetry Ingestion (Priority: P1)

As a tracking camper, I want to use the live admin portal (`https://emf.harvinderatwal.com/admin.html`) to log activities (e.g. drinks, status updates) and have them instantly processed and securely saved in a live cloud database.

**Why this priority**: User testing requires functional backend ingestion so participants can generate real-world data flows.

**Independent Test**: Use the live admin page to submit a "Drinks" log. Verify that the browser receives a `201 Created` response from the live API Gateway and the public dashboard updates to reflect the new total.

**Acceptance Scenarios**:

1. **Given** the live admin portal is loaded, **When** a user submits a valid log with the correct `tracker_key`, **Then** the live API Gateway routes the request to a Python Lambda, which securely updates the live Amazon DynamoDB tables.
2. **Given** a user attempts to submit a log with an invalid `tracker_key`, **Then** the live API Gateway/Lambda rejects the request with a `401 Unauthorized` response to protect the production database from spam.

---

### User Story 3 - Infrastructure Provisioning and Teardown (Priority: P2)

As a DevOps engineer, I want to be able to provision, update, and fully tear down the entire production AWS environment using simple Terraform commands (`terraform apply` and `terraform destroy`), so that I can manage infrastructure predictably without clicking through the AWS console.

**Why this priority**: Adherence to Constitution Principle III (Infrastructure-as-Code) and enables rapid recovery or environment recreation.

**Independent Test**: Execute `terraform plan` in the `tf/` directory and verify that it outputs a clean execution plan for creating/updating the S3, CloudFront, Lambda, API Gateway, and DynamoDB resources without manual interventions.

**Acceptance Scenarios**:

1. **Given** the Terraform configuration files are complete, **When** `terraform apply` is executed, **Then** all required AWS resources are created and configured correctly.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (S3 & CloudFront Frontend)**: The system MUST provision an Amazon S3 bucket configured for static website hosting and an AWS CloudFront distribution to serve the `web/` assets globally over HTTPS (Principle VII). All core regional resources MUST reside in the UK (London) region (`eu-west-2`).
- **FR-002 (API Gateway)**: The system MUST provision an AWS API Gateway v2 (HTTP API) configured with proper CORS policies allowing requests from the production CloudFront domain (e.g., `emf.harvinderatwal.com`).
- **FR-003 (Lambda Provisioning)**: The system MUST provision Python 3.12 AWS Lambda functions to handle backend logic, packaging the code from the `backend/` directory, and attach them to the correct API Gateway routes.
- **FR-004 (DynamoDB Setup)**: The system MUST provision a single Amazon DynamoDB table configured for On-Demand capacity with a composite key structure (`event` as Partition Key, `type` as Sort Key) (Principle IV).
- **FR-005 (Secrets Management)**: The system MUST provision an AWS Secrets Manager secret to securely store the `tracker_key` and other sensitive credentials, making them accessible to the Lambda functions at runtime (Principle V).
- **FR-006 (Custom Domain & SSL)**: The system MUST configure the CloudFront distribution with the custom domain `emf.harvinderatwal.com` and an associated AWS Certificate Manager (ACM) SSL certificate. Since DNS is managed externally in Cloudflare, Terraform MUST output the required DNS validation records (for ACM) and the CloudFront distribution domain name so they can be manually added to Cloudflare.
- **FR-007 (Frontend API URL Binding)**: The frontend JavaScript MUST be updated/configured to dynamically target the live API Gateway endpoint URL when deployed to production.
- **FR-008 (CI/CD Automated Deployment)**: The system MUST include a GitHub Actions CI/CD workflow (`.github/workflows/deploy.yml`) triggered on pushes to the `main` branch that automates setting up Terraform, applying AWS resources, syncing frontend static assets (`web/`) to S3, and invalidating CloudFront distribution caches.

### Key Entities

*None specific to this feature, as it provisions infrastructure rather than application data models.*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the AWS infrastructure is deployed successfully via `terraform apply` with zero manual configuration steps required in the AWS Console.
- **SC-002**: The production frontend at `https://emf.harvinderatwal.com` loads fully in under 2 seconds on standard mobile connections.
- **SC-003**: Live telemetry POST requests to the production API process and return within 500ms (P95 latency).

## Assumptions

- **Assumption 1**: The AWS CLI is installed and configured with appropriate administrator credentials on the deployment machine.
- **Assumption 2**: Terraform is installed on the deployment machine.
- **Assumption 3**: The required SSL certificate for `emf.harvinderatwal.com` can be provisioned in the `us-east-1` region (required for CloudFront).
ndon) region (`eu-west-2`) to ensure optimal latency and residency compliance.
