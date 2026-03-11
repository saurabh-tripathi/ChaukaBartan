output "app_url" {
  description = "Public URL of the app"
  value       = local.domain_name != "" ? "https://${local.domain_name}" : "http://${module.alb.alb_dns_name}"
}

output "ecr_repository_url" {
  description = "Push backend Docker image here"
  value       = module.ecr.repository_url
}

output "ecr_frontend_repository_url" {
  description = "Push frontend Docker image here"
  value       = module.ecr.frontend_repository_url
}

output "rds_address" {
  description = "RDS host (for tunnelling / migrations)"
  value       = module.rds.address
}

output "ecs_cluster" {
  value = module.ecs.cluster_name
}

output "ecs_service" {
  description = "Backend ECS service"
  value       = module.ecs.service_name
}

output "ecs_frontend_service" {
  description = "Frontend ECS service"
  value       = module.ecs.frontend_service_name
}

output "log_group" {
  description = "CloudWatch log group — backend"
  value       = module.ecs.log_group_name
}

output "frontend_log_group" {
  description = "CloudWatch log group — frontend"
  value       = module.ecs.frontend_log_group_name
}

output "route53_name_servers" {
  description = "Copy these 4 NS records into GoDaddy → gradnuclei.com → Nameservers → Custom DNS"
  value       = var.root_domain != "" ? module.dns[0].name_servers : []
}
