# Quickstart Validation Guide: Production Infrastructure Deployment

This guide describes how to run Terraform commands to provision, update, or tear down the production AWS environment, and how to configure DNS records in Cloudflare.

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

Upon successful completion, Terraform will output your Cloudflare validation parameters.

---

## 3. Cloudflare DNS Configuration

Copy the outputs printed on your terminal and add them manually to Cloudflare:

1. **SSL Validation Record**:
   * **Type**: `CNAME`
   * **Name**: Use the output value `acm_validation_name`
   * **Target**: Use the output value `acm_validation_value`
   * **Proxy Status**: `DNS Only` (Grey Cloud)
2. **Dashboard Domain Mapping**:
   * **Type**: `CNAME`
   * **Name**: `emf`
   * **Target**: Use the output value `cloudfront_domain_name` (e.g., `d123456.cloudfront.net`)
   * **Proxy Status**: `Proxied` (Orange Cloud)

---

## 4. Tearing Down the Infrastructure

To completely destroy all production resources, ensuring zero future billing charges on AWS, execute:
```bash
terraform destroy
```
Confirm with `yes` to finalize the teardown.
