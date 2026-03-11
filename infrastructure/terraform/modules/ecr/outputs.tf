output "repository_url"          { value = aws_ecr_repository.app.repository_url }
output "repository_arn"          { value = aws_ecr_repository.app.arn }
output "frontend_repository_url" { value = aws_ecr_repository.frontend.repository_url }
output "frontend_repository_arn" { value = aws_ecr_repository.frontend.arn }
