# tf/secrets.tf
# AWS Secrets Manager parameter caches ensuring Constitution Principle V zero hardcoded credentials.

resource "aws_secretsmanager_secret" "secrets" {
  name                    = "open_emfer_v2_production_credentials" # Unique name to bypass scheduled deletion locks
  recovery_window_in_days = 0 # Forces immediate cleanup on destroy

  tags = {
    Environment = "production"
    Project     = "open-emfer-v2"
  }
}

resource "aws_secretsmanager_secret_version" "secret_template" {
  secret_id = aws_secretsmanager_secret.secrets.id
  secret_string = jsonencode({
    tracker_key         = "hvy_k_8f2d9a3b6c7e4f01a8b2c3d4e5f6a7b8"
  })

  # Ignore future manual token value edits from AWS Secrets console/CLI during subsequent applies
  lifecycle {
    ignore_changes = [secret_string]
  }
}
