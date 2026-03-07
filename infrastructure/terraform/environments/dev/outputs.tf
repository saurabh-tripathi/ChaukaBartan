# Print these after `terraform apply` to know where to point your browser/app

output "app_url" {
  description = "Public URL of the app (HTTP for now; add HTTPS + custom domain later)"
  value       = "http://${module.alb.alb_dns_name}"
}

output "ecr_repository_url" {
  description = "Push your Docker image here"
  value       = module.ecr.repository_url
}

output "rds_address" {
  description = "RDS host (for local tunnelling / migrations)"
  value       = module.rds.address
}

output "ecs_cluster" {
  value = module.ecs.cluster_name
}

output "ecs_service" {
  value = module.ecs.service_name
}

output "log_group" {
  description = "CloudWatch log group for app logs"
  value       = module.ecs.log_group_name
}
