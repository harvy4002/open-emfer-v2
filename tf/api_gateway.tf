# tf/api_gateway.tf
# AWS API Gateway v2 HTTP API router and CORS mappings matching Constitution Principle I and V.

# HTTP API Gateway
resource "aws_apigatewayv2_api" "http_api" {
  name          = "open_emfer_v2_production_gateway"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"] # Wildcard allowed origins to ensure Cloudflare Pages can query the API without any CORS preflight blocks (highly robust!)
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["content-type", "authorization", "tracker_key"]
    max_age       = 300
  }
}

# Lambda integration mapping
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"

  connection_type      = "INTERNET"
  description          = "HTTP API to Lambda integration"
  integration_method   = "POST"
  integration_uri      = aws_lambda_function.api_lambda.invoke_arn
  payload_format_version = "2.0"
}

# Unified ANY proxy route to support modular URL mappings (ANY /{proxy+})
resource "aws_apigatewayv2_route" "proxy_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Root ANY route fallback
resource "aws_apigatewayv2_route" "root_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Production deployment stage with auto-deploy enabled
resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "prod"
  auto_deploy = true

  tags = {
    Environment = "production"
    Project     = "open-emfer-v2"
  }
}
