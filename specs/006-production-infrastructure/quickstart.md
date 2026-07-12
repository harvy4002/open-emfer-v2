# Quickstart Validation Guide: Production Infrastructure Deployment (Cloudflare Proxy)

This guide describes how to run Terraform commands to provision, update, or tear down the production AWS environment, and how to configure CNAME records and Origin Rules in Cloudflare (Path A).

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

Upon successful completion, Terraform will output your CloudFront CDN endpoint URL.

---

## 3. Cloudflare DNS & Origin Rule Configuration

Copy the outputs printed on your terminal and configure them in your Cloudflare dashboard:

### Step A: Configure CNAME Record
1. Log in to Cloudflare and open the DNS settings for `harvinderatwal.com`.
2. Add a new DNS record:
   * **Type**: `CNAME`
   * **Name**: `emf`
   * **Target**: Use the output value `cloudfront_domain_name` (e.g., `d12345abcdef.cloudfront.net`)
   * **Proxy Status**: `Proxied` (Orange Cloud) - This enables Cloudflare's universal SSL on the custom domain.
3. Save the record.

### Step B: Configure Cloudflare Origin Rule (Host Header Override)
Because CloudFront expects the request `Host` header to match the CloudFront distribution domain name (and we did not configure Alternate Domain Names in AWS to keep everything regional in London), we must tell Cloudflare to overwrite the request's Host header when proxying requests to AWS.

1. In the Cloudflare left-hand navigation pane, go to **Rules → Origin Rules**.
2. Click **Create Rule**:
   * **Rule Name**: `EMF AWS Host Override`
   * **When incoming requests match... (Field)**: `Hostname`
   * **Operator**: `equals`
   * **Value**: `emf.harvinderatwal.com`
   * **Choose an action... (Host Header)**: Select **Override**
   * **Value**: Set static value to your CloudFront distribution domain name (e.g. `d12345abcdef.cloudfront.net`, copied from `cloudfront_domain_name` output)
3. Click **Deploy**.

*Traffic to `https://emf.harvinderatwal.com` will now resolve instantly and securely over HTTPS through Cloudflare to your London-deployed AWS bucket!*

---

## 4. Tearing Down the Infrastructure

To completely destroy all production resources, ensuring zero future billing charges on AWS, execute:
```bash
terraform destroy
```
Confirm with `yes` to finalize the teardown.
