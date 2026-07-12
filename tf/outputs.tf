# tf/outputs.tf
# Surfaces key mapping properties to connect client scripts and external hosting environments.

output "api_gateway_endpoint_url" {
  value       = aws_apigatewayv2_stage.prod.invoke_url
  description = "Live HTTPS production endpoint of your backend API Gateway."
}
