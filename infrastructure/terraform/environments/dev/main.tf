locals {
  # If app_image isn't provided yet, use a lightweight placeholder so the ECS
  # service can be created. Tasks will fail health checks until you push a real
  # image, but the rest of the infrastructure is fully functional.
  app_image = var.app_image != "" ? var.app_image : "${module.ecr.repository_url}:latest"
}

# ── Random passwords (stored in Terraform state — encrypted at rest) ───────────

resource "random_password" "db" {
  length  = 24
  special = false  # avoid chars that break connection string parsing
}

resource "random_password" "secret_key" {
  length  = 64
  special = false
}

# ── Modules ───────────────────────────────────────────────────────────────────

module "vpc" {
  source       = "../../modules/vpc"
  project_name = var.project_name
  environment  = var.environment
}

module "ecr" {
  source       = "../../modules/ecr"
  project_name = var.project_name
  environment  = var.environment
}

module "rds" {
  source       = "../../modules/rds"
  project_name = var.project_name
  environment  = var.environment

  subnet_ids  = module.vpc.isolated_subnet_ids
  rds_sg_id   = module.vpc.rds_sg_id
  db_name     = var.db_name
  db_username = var.db_username
  db_password = random_password.db.result
}

module "secrets" {
  source       = "../../modules/secrets"
  project_name = var.project_name
  environment  = var.environment

  # DATABASE_URL constructed from live RDS outputs — no manual step needed
  database_url = "postgresql://${var.db_username}:${random_password.db.result}@${module.rds.address}:${module.rds.port}/${module.rds.db_name}"
  secret_key   = random_password.secret_key.result
}

module "alb" {
  source       = "../../modules/alb"
  project_name = var.project_name
  environment  = var.environment

  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.public_subnet_ids
  alb_sg_id      = module.vpc.alb_sg_id
  domain_name    = var.domain_name
  hosted_zone_id = var.hosted_zone_id
}

module "ecs" {
  source       = "../../modules/ecs"
  project_name = var.project_name
  environment  = var.environment
  region       = var.region

  app_image     = local.app_image
  subnet_ids    = module.vpc.public_subnet_ids
  ecs_sg_id     = module.vpc.ecs_sg_id

  target_group_arn         = module.alb.target_group_arn
  database_url_secret_arn  = module.secrets.database_url_secret_arn
  secret_key_arn           = module.secrets.secret_key_arn
  ecr_repository_arn       = module.ecr.repository_arn
}
