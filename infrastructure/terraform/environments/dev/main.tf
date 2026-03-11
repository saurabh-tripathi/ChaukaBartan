locals {
  # Full domain for this project: chaukabartan.gradnuclei.com
  domain_name = var.root_domain != "" ? "${var.subdomain}.${var.root_domain}" : ""

  # Placeholder images for first apply (before real images are pushed)
  app_image      = var.app_image      != "" ? var.app_image      : "${module.ecr.repository_url}:latest"
  frontend_image = var.frontend_image != "" ? var.frontend_image : "${module.ecr.frontend_repository_url}:latest"
}

# ── Random secrets ────────────────────────────────────────────────────────────

resource "random_password" "db" {
  length  = 24
  special = false
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

module "dns" {
  count        = var.root_domain != "" ? 1 : 0
  source       = "../../modules/dns"
  project_name = var.project_name
  environment  = var.environment
  root_domain  = var.root_domain
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

  database_url = "postgresql://${var.db_username}:${random_password.db.result}@${module.rds.address}:${module.rds.port}/${module.rds.db_name}"
  secret_key   = random_password.secret_key.result
  app_password = var.app_password
}

module "alb" {
  source       = "../../modules/alb"
  project_name = var.project_name
  environment  = var.environment

  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.public_subnet_ids
  alb_sg_id      = module.vpc.alb_sg_id
  domain_name    = local.domain_name
  hosted_zone_id = var.root_domain != "" ? module.dns[0].zone_id : ""
}

module "ecs" {
  source       = "../../modules/ecs"
  project_name = var.project_name
  environment  = var.environment
  region       = var.region

  app_image      = local.app_image
  frontend_image = local.frontend_image

  subnet_ids                = module.vpc.public_subnet_ids
  ecs_sg_id                 = module.vpc.ecs_sg_id
  backend_target_group_arn  = module.alb.backend_target_group_arn
  frontend_target_group_arn = module.alb.frontend_target_group_arn

  database_url_secret_arn = module.secrets.database_url_secret_arn
  secret_key_arn          = module.secrets.secret_key_arn
  app_password_secret_arn = module.secrets.app_password_secret_arn
  ecr_repository_arn      = module.ecr.repository_arn
}
