# Technical Research: Production Infrastructure Deployment

This document outlines the architectural decisions, Cloudflare DNS configuration patterns, and Lambda deployment workflows chosen to provision our production AWS ecosystem.

---

## 1. CloudFront Custom Domain & ACM Certificate Region

### Decision
The AWS Certificate Manager (ACM) SSL certificate for `emf.harvinderatwal.com` MUST be created in the `us-east-1` (N. Virginia) region. The CloudFront distribution will reference this certificate ARN.

### Rationale
- **CloudFront ACM Requirement**: AWS enforces a strict constraint that any SSL certificate used by Amazon CloudFront MUST reside in the `us-east-1` region, regardless of where the other resources (like API Gateway or Lambda) are located.
- **Provider Aliases in Terraform**: To support this in Terraform, we configure a secondary AWS provider alias targeting `us-east-1` specifically for the `aws_acm_certificate` and `aws_acm_certificate_validation` resources, while the main provider remains in the developer's default home region (e.g., `eu-west-2` or `us-west-2`).

### Alternatives Considered
- **S3 Hosting Without CloudFront**: Rejected. S3 does not support SSL/HTTPS natively for custom domains (e.g. S3 static websites can only be queried over HTTP if mapped directly to DNS). HTTPS is non-negotiable for secure field operation and modern browser security.

---

## 2. External DNS Mapping (Cloudflare)

### Decision
Terraform will not manage DNS records directly (no `aws_route53_record` resources). Instead, the ACM validation records and CloudFront CNAME records will be surfaced as explicit Terraform outputs (`outputs.tf`). These values must be copied and pasted manually into the Cloudflare DNS dashboard.

### Required DNS Configurations in Cloudflare:
1. **ACM Certificate Validation Record**: A `CNAME` record mapping the ACM-generated key to the AWS validation endpoint.
2. **Dashboard Domain Mapping**: A `CNAME` record pointing `emf.harvinderatwal.com` to the CloudFront distribution domain name (e.g., `d1234567abcdef.cloudfront.net`). Ensure that the Cloudflare DNS proxy mode is configured properly (e.g., DNS-only or Proxied) depending on SSL redirection parameters.

### Rationale
- **Governance Isolation (Principle I)**: Since Cloudflare is an external third-party provider, decoupling DNS management from AWS-specific Terraform configurations reduces deployment credential requirements and minimizes Route53 hosting fees.

---

## 3. Lambda Bundling & Execution Policies (IAM)

### Decision
Utilize the Terraform `archive_file` resource to dynamically compress Python source files in the `backend/` directory into zip archives on the fly. These zip files will be uploaded directly to AWS Lambda with an execution IAM role mapped to the `AWSLambdaBasicExecutionRole` policy and least-privilege DynamoDB/SecretsManager access.

### Rationale
- **Serverless Simplicity (Principle II)**: Packing Lambdas inside the standard zip format avoids needing to manage container registries (ECR) or compile heavy Docker files, ensuring deployment boots in seconds with minimal maintenance overhead.
- **Security Isolation (Principle V)**: Strict IAM boundaries block Lambdas from modifying infrastructure, limiting actions exclusively to querying the specific DynamoDB table and Secrets Manager values.
