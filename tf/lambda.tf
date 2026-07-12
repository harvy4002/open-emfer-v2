# tf/lambda.tf
# AWS Lambda function provisioning, zip code packaging, and least-privilege execution roles.

# Create zip archive of backend directory on-the-fly
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../backend"
  output_path = "${path.module}/lambda_function_payload.zip"
  excludes    = ["__pycache__", "*.pyc", "index.html"] # Filter local caches and examples
}

# IAM Role for Lambda execution matching Constitution Principle V zero-trust
resource "aws_iam_role" "lambda_role" {
  name = "open_emfer_v2_production_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# CloudWatch Logging policy attachment
resource "aws_iam_role_policy_attachment" "basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lease privilege DynamoDB and Secrets Manager access policy (Principle V)
resource "aws_iam_policy" "lambda_privileges" {
  name        = "open_emfer_v2_production_lambda_privileges"
  description = "Allows Lambda to write/read target DynamoDB table and pull Secrets Manager credentials."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.table.arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.secrets.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "custom_privileges" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_privileges.arn
}

# Unified serverless Lambda function running Python 3.12 (Principle II)
resource "aws_lambda_function" "api_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "open_emfer_v2_production_api"
  role             = aws_iam_role.lambda_role.arn
  handler          = "sim_server.run" # Or entrypoint lambda router
  runtime          = "python3.12"
  timeout          = 15
  memory_size      = 256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.table.name
      SECRETS_NAME        = aws_secretsmanager_secret.secrets.name
    }
  }

  tags = {
    Environment = "production"
    Project     = "open-emfer-v2"
  }
}

# Allow API Gateway to invoke the Lambda function
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.arn}/*/*"
}
