<!--
### Sync Impact Report
- Version change: 1.2.0 → 1.3.0
- List of modified principles:
  - Principle VI: Automated Testing and Mocking (Expanded to forbid silent exception swallowing in local/development runs)
  - Principle VIII: Fast Feedback Cycles (Expanded to mandate real-time CloudWatch log tailing CLI commands)
- Added sections: None
- Templates requiring updates: None
- Follow-up TODOs: None
-->
# Open EMF Camper Constitution

## Core Principles

### I. Contract-First Development (The Source of Truth)
The OpenAPI specification (`openapi.json`) and Spec Kit Markdown specifications (`specs/*.md`) are the non-negotiable sources of truth for the entire application. No endpoint, query parameter, request body, or header may be introduced in the codebase (Lambdas or Terraform) unless it has been explicitly defined in the API contract first.

### II. Serverless Simplicity (Lightweight Python Lambdas)
Backend services MUST be built as lightweight, single-responsibility Python Lambda functions (Python 3.12+). 
- Avoid heavy runtime frameworks or bloated dependencies. 
- Use the AWS SDK (`boto3`) and Python standard library primitives for maximum speed, cold-start mitigation, and simplicity.
- Code must remain modular, readable, and strictly typed where possible.

### III. Infrastructure-as-Code (Terraform Only)
Every infrastructure resource—including AWS Lambda functions, API Gateway v2 HTTP APIs, DynamoDB tables, IAM roles, S3 buckets, and Secrets Manager variables—MUST be modeled and provisioned strictly through Terraform (`tf/`). No manual infrastructure configuration is permitted in the AWS Console, ensuring 100% reproducible environments.

### IV. Safe and Secure Database Modeling (DynamoDB Keys)
Data modeling in DynamoDB must strictly use the single-table or composite-key pattern:
- The Partition Key MUST be `event` and the Sort Key MUST be `type`.
- Accumulators and history-tracking (such as coordinate sequences or cumulative steps) must maintain strict array sizing bounds (e.g. maximum of 20 coordinate entries) to optimize performance, cost, and payload size.

### V. Zero-Trust Security & Secrets Management
Sensitive credentials, tokens, or API keys (such as Monzo OAuth credentials or device tracker keys) MUST NEVER be committed to version control or hardcoded in resource scripts.
- Private third-party secrets must reside exclusively in AWS Secrets Manager and be loaded dynamically at runtime.
- Telemetry mutative operations (POST) must strictly authenticate incoming traffic against a secure header-based token (`tracker_key`).

### VI. Automated Testing and Mocking (No Silent Failures)
All Lambda handlers and logic branches MUST be covered by unit tests (using `pytest` or `unittest`) prior to merging.
- Third-party APIs, AWS DynamoDB, and Secrets Manager services must be fully mocked (using libraries like `moto` or standard Python mock decorators) to verify functionality offline.
- **No Silent Exception Swallowing**: Exceptions in the backend or simulation handlers MUST NEVER be caught and swallowed silently without proper logging or error propagation. In local/development testing runs, Exceptions MUST be actively raised (rather than returning default empty states like `[]` or `"normal"`) to force fast failures and detect configuration or SDK mismatches immediately.

### VII. Cost-Optimized Serverless Frontends (S3 & CloudFront Static Sites)
To keep hosting costs near zero and maximize load performance on mobile networks, both the public telemetry dashboard and the participant manual logging/admin views MUST be developed as highly responsive, lightweight, mobile-first static web applications.
- All user-facing pages, charts, and administrative panels MUST be compiled/built as static assets (HTML/CSS/JS) and hosted in Amazon S3 buckets distributed via AWS CloudFront CDN with caching enabled.
- Avoid server-side rendering (SSR) or active container/server hosting to eliminate dynamic server running costs.
- Dynamic data interactions, live charts, and administrative manual logging forms MUST query the serverless AWS API Gateway / Lambda backend via browser-native fetch calls.
- Enforce secure token authentication (`tracker_key`) on all client-initiated mutative API requests.

### VIII. Fast Feedback Cycles (Local Simulation & Production Observability)
The codebase and design configurations MUST facilitate an ultra-fast developer feedback loop, allowing developers and automated agents to run, test, and debug both frontend static interfaces and backend API endpoints locally without relying on live AWS cloud deployments.
- **Local API Simulation**: Both backend Lambdas and API Gateway route behaviors must be runnable locally (e.g., using lightweight offline emulation or simple python/go dev servers), enabling manual payload submits and state lookups.
- **Manual Data Flow Triggering**: Maintain explicit, runnable testing shell scripts (such as custom cURL triggers) and local browser configuration states that can manually inject mock payloads into ingestion endpoints, allowing instant verification of end-to-end data flows locally.
- **Real-Time Production Observability (Log Tailing)**: Developers and testing agents MUST maintain clean CLI commands to tail live CloudWatch Logs streams in real-time (using standard `aws logs tail` utility calls with specified custom profiles like `--profile open-emfer`). This ensures any server-side syntax errors, attribute crashes (such as `AttributeError` SDK mismatches), or permission blocks can be diagnosed instantly as they occur during production verification checks.
- **Rationale**: Mitigates downstream integration flaws, drastically decreases developer validation cycle times from minutes/hours of Terraform provisioning to sub-second local iterations, and ensures high operational readiness before production pushes.

---

## Technical Constraints & Standards

- **Backend Runtime**: Python 3.12 or newer.
- **Database**: Amazon DynamoDB (On-Demand capacity).
- **Hosting / Gateways**: AWS API Gateway HTTP APIs with proxy integrations. Static assets hosted on Amazon S3 and served via CloudFront CDN to minimize costs and maximize mobile performance.
- **Python Formatting**: Strict compliance with PEP 8 standards. Code should be automatically formatted with `ruff` or `black` before execution.
- **Frontend Assets**: Responsive, mobile-friendly Vanilla HTML/CSS (using Bulma CSS for responsive visual layouts). Zero complex frontend build pipelines or heavy frameworks to preserve serverless simplicity and keep browser loading times minimal (<2s) on slow camper networks.

---

## Development Workflow & Quality Gates

1. **Specify**: Write/update the feature specification (`specs/[feature].md`) outlining acceptance scenarios, edge cases, and the API schemas.
2. **Review Contract**: Synchronize and update the global `openapi.json` contract to reflect any schema modifications.
3. **Plan**: Formulate the detailed technical blueprint (`specs/[feature].plan.md`) describing precise database migrations, Lambda changes, and Terraform adjustments.
4. **Implement**: Write the clean implementation, strictly conforming to the design patterns and unit testing requirements.
5. **Validate**:
   - Run Python unit tests and formatting linters.
   - Run `terraform validate` inside the `tf/` folder to ensure system integrity.

---

## Governance

This Constitution supersedes all standard development ad-hoc patterns. Any changes to core principles, tech stacks, or architectural rules require documentation, ratification by the project owner, and updating this file.

**Version**: 1.3.0 | **Ratified**: 2026-07-04 | **Last Amended**: 2026-07-14
