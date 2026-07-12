# tf/outputs.tf
# Surfaces key mapping properties to configure Cloudflare external DNS and connect client scripts.

output "acm_validation_name" {
  value       = tolist(aws_acm_certificate.cert.domain_validation_options)[0].resource_record_name
  description = "CNAME record Name to add in Cloudflare DNS for SSL certificate validation."
}

output "acm_validation_value" {
  value       = tolist(aws_acm_certificate.cert.domain_validation_options)[0].resource_record_value
  description = "CNAME record Value to add in Cloudflare DNS for SSL certificate validation."
}

output "cloudfront_domain_name" {
  value       = aws_cloudfront_distribution.cdn.domain_name
  description = "Target domain name of the CloudFront distribution to point emf.harvinderatwal.com CNAME to."
}

output "api_gateway_endpoint_url" {
  value       = aws_apigatewayv2_stage.prod.invoke_url
  description = "Live HTTPS production endpoint of your backend API Gateway."
}
