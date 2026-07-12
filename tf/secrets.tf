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
    tracker_key         = "mock-super-secret-key"
    monzo_client_id     = "oauth-client-id-here"
    monzo_client_secret = "oauth-client-secret-here"
  })

  # Ignore future manual token value edits from AWS Secrets console/CLI during subsequent applies
  lifecycle {
    ignore_changes = [secret_string]
  }
}
