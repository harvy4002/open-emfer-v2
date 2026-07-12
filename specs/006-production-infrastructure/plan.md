# Implementation Plan: Production Infrastructure Deployment

**Branch**: `006-production-infrastructure` | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/006-production-infrastructure/spec.md`

**Note**: This plan establishes the Terraform module architectures, IAM role definitions, API route integrations, and Cloudflare external DNS output mappings to fulfill all serverless hosting principles of the Constitution.

## Summary

This feature delivers the complete Infrastructure-as-Code (IaC) configuration to deploy the Open EMF Camper application live on AWS:
1. **S3 Static Website Bucket**: Stores `web/` assets (`index.html`, `admin.html`, js/css assets).
2. **AWS CloudFront Distribution**: Serves static pages globally with SSL (via AWS Certificate Manager) under `emf.harvinderatwal.com`.
3. **AWS API Gateway v2**: Manages high-speed serverless HTTP routing pointing to AWS Lambda.
4. **AWS Lambda**: Hosts Python 3.12 runtime logic for `/beer`, `/sensecap`, `/browan`, `/monzo`, and `/history` handlers.
5. **Amazon DynamoDB**: Operates a single composite-key table for telemetry and aggregates storage.
6. **AWS Secrets Manager**: Caches and secures Monzo bank OAuth keys and gateway secret parameters.
7. **Cloudflare External Mapping**: Terraform outputs CloudFront CNAME, CloudFront ID, and S3 bucket name to allow easy automated CI/CD static syncing and CDN cache invalidations.

## Technical Context

**Language/Version**: Terraform v1.5+, Python 3.12+ (AWS Lambda), Vanilla HTML5/CSS3/ES6+.

**Primary Dependencies**: HashiCorp AWS Provider v5+.

**Storage**: Amazon DynamoDB (On-Demand capacity) and local JSON DB state for fallback developer emulations.

**Testing**: `terraform validate`, `pytest` for Lambda handlers, browser DNS query lock validations.

**Target Platform**: Amazon Web Services (AWS) global cloud infrastructure.

**Project Type**: Infrastructure-as-Code.

**Performance Goals**: Provision all active cloud resources in < 15 minutes, with CloudFront edge response latency < 2s (SC-002).

**Constraints**:
* Strict IAM least-privilege policies—Lambda roles can only query and write to their designated DynamoDB tables and Secrets Manager records.
* All core AWS resources are hosted natively inside the UK (London) region (`eu-west-2`), ensuring 100% regional data residency.
* CORS headers strictly defined to only accept the CloudFront domain origin.

**Scale/Scope**: Production-grade camp-wide telemetry pipeline with zero idle cost.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Standard | Status | Verification & Alignment |
| :--- | :--- | :--- |
| **I. Contract-First Development** | ✅ PASS | API Gateway routes strictly align with endpoints declared in `openapi.json`. |
| **II. Serverless Simplicity** | ✅ PASS | Built on native pay-per-use AWS Lambda and API Gateway HTTP proxies (zero idle cost). |
| **III. Infrastructure-as-Code** | ✅ PASS | Every single AWS resource is modeled and provisioned strictly via Terraform under `tf/`. |
| **IV. Safe Database Keys** | ✅ PASS | DynamoDB configuration defines Partition Key (`event`) and Sort Key (`type`) structures. |
| **V. Zero-Trust Security** | ✅ PASS | IAM roles strictly block cross-privilege, and Secrets Manager stores all Monzo / gateway keys. |
| **VI. Automated Testing** | ✅ PASS | Pytest covers mock boto3 table writes; Terraform configurations are validated before push. |
| **VII. Cost-Optimized Frontends**| ✅ PASS | S3 static hosting bucket fronted by CloudFront edge caches results in zero server run costs. |
| **VIII. Fast Feedback Cycles** | ✅ PASS | Infrastructure includes simple outputs to easily map URLs and validation keys. |

## Project Structure

### Documentation (this feature)

```text
specs/006-production-infrastructure/
├── spec.md              # Feature specification
├── plan.md              # Technical implementation plan
├── research.md          # Technical research and choices
├── data-model.md        # DB Partition mappings
├── quickstart.md        # Scenario testing and validation guide
└── checklists/
    └── requirements.md  # General spec quality checklist
```

### Source Code (repository root)

```text
tf/
├── main.tf              # AWS Provider and variables
├── s3_cloudfront.tf     # S3 website bucket & CloudFront distribution
├── api_gateway.tf       # API Gateway routes & CORS mappings
├── lambda.tf            # Lambda handlers bundling, variables, & IAM execution roles
├── dynamodb.tf          # DynamoDB table definition
├── secrets.tf           # AWS Secrets Manager records
└── outputs.tf           # Print ACM DNS validation record and CloudFront CNAME
```

**Structure Decision**: Infrastructure code grouped inside the existing `tf/` directory to preserve clean architectural modularity.

## Complexity Tracking

*No Constitution violations detected. The serverless, infrastructure-as-code design is 100% compliant with Open EMF Camper architectural parameters.*
tectural parameters.*
