# tf/dynamodb.tf
# Amazon DynamoDB composite key database table definitions matching Constitution Principle IV.

resource "aws_dynamodb_table" "table" {
  name         = "open_emfer_v2_production"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "event"
  range_key    = "type"

  attribute {
    name = "event"
    type = "S"
  }

  attribute {
    name = "type"
    type = "S"
  }

  tags = {
    Environment = "production"
    Project     = "open-emfer-v2"
  }
}
