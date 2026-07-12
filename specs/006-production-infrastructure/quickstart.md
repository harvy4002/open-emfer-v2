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

Perform a dry run to verify the resources to be created:
```bash
terraform plan
```

Execute the live provisioning command. Confirm with `yes` when prompted:
```bash
terraform apply
```

Upon successful completion, Terraform will output your CloudFront CNAME values and SSL validation records.

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
