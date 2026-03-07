locals {
  prefix = "${var.project_name}/${var.environment}"
  tags   = { Project = var.project_name, Environment = var.environment }
}

resource "aws_secretsmanager_secret" "database_url" {
  name                    = "${local.prefix}/database_url"
  recovery_window_in_days = 0  # allow immediate deletion in dev
  tags                    = local.tags
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = var.database_url
}

resource "aws_secretsmanager_secret" "secret_key" {
  name                    = "${local.prefix}/secret_key"
  recovery_window_in_days = 0
  tags                    = local.tags
}

resource "aws_secretsmanager_secret_version" "secret_key" {
  secret_id     = aws_secretsmanager_secret.secret_key.id
  secret_string = var.secret_key
}
