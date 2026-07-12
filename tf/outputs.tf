# tf/outputs.tf
# Surfaces key mapping properties to configure Cloudflare external DNS and connect client scripts.

output "cloudfront_domain_name" {
  value       = aws_cloudfront_distribution.cdn.domain_name
  description = "Target domain name of the CloudFront distribution to point emf.harvinderatwal.com CNAME to in Cloudflare."
}

output "cloudfront_distribution_id" {
  value       = aws_cloudfront_distribution.cdn.id
  description = "The unique ID of the CloudFront distribution to trigger cache invalidations during CI/CD pushes."
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.frontend.id
  description = "The target Amazon S3 website hosting bucket name."
}

output "api_gateway_endpoint_url" {
  value       = aws_apigatewayv2_stage.prod.invoke_url
  description = "Live HTTPS production endpoint of your backend API Gateway."
}
