output "database_url_secret_arn" { value = aws_secretsmanager_secret.database_url.arn }
output "secret_key_arn"          { value = aws_secretsmanager_secret.secret_key.arn }
output "app_password_secret_arn" { value = aws_secretsmanager_secret.app_password.arn }
