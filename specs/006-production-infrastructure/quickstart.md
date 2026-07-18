# Quickstart Validation Guide: Production Infrastructure Deployment (AWS ACM SSL)

This guide describes how to run Terraform commands to provision, update, or tear down the production AWS environment, and how to configure CNAME records in Cloudflare (Path B).

---

## 1. Initializing the Project

Open your terminal and navigate to the Terraform configurations folder:
```bash
cd tf/
terraform init
```

---

## 2. Planning and Deploying to AWS

All Terraform changes MUST go through the GitHub Actions deployment pipeline (`.github/workflows/deploy.yml`) on a push to `main` and MUST NEVER be run or applied directly from local developer environments.

### Local Planning / Dry Run
To safely verify the resources that would be created or modified by the pipeline, navigate to the `tf/` folder and run a dry-run plan locally:
```bash
terraform plan
```

### Live Deployments (CI/CD Pipeline)
Once your changes are verified and committed, push them to the `main` branch to trigger the automated GitHub Actions deployment. Local `terraform apply` executions are strictly prohibited to ensure environment consistency and state integrity.

---

## 3. Cloudflare DNS Configuration

Copy the outputs printed on your terminal and add them to your Cloudflare DNS settings:

### Step A: Configure SSL Validation Record (CNAME)
To allow AWS Certificate Manager (ACM) to validate ownership of your domain and issue your SSL certificate:
1. Log in to Cloudflare and open the DNS settings for `harvinderatwal.com`.
2. Add a new DNS record:
   * **Type**: `CNAME`
   * **Name**: Use the output value `acm_validation_name`
   * **Target**: Use the output value `acm_validation_value`
   * **Proxy Status**: `DNS Only` (Grey Cloud) - **Crucial**: Must be un-proxied during initial validation.
3. Save the record.

### Step B: Configure Dashboard Domain Mapping (CNAME)
To point your custom subdomain `emf.harvinderatwal.com` to the CloudFront distribution:
1. Add a second DNS record:
   * **Type**: `CNAME`
   * **Name**: `emf`
   * **Target**: Use the output value `cloudfront_domain_name` (e.g., `d12345abcdef.cloudfront.net`)
   * **Proxy Status**: `Proxied` (Orange Cloud) - Enables Cloudflare's edge security.
2. Save the record.

*Once AWS validates the CNAME (usually takes 5 minutes), your site is fully operational over HTTPS at `https://emf.harvinderatwal.com`!*

---

## 4. Tearing Down the Infrastructure

To completely destroy all production resources, ensuring zero future billing charges on AWS, execute:
```bash
terraform destroy
```
Confirm with `yes` to finalize the teardown.
