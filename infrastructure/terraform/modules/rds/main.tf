locals {
  name = "${var.project_name}-${var.environment}"
  tags = { Project = var.project_name, Environment = var.environment }
}

resource "aws_db_subnet_group" "this" {
  name       = local.name
  subnet_ids = var.subnet_ids
  tags       = merge(local.tags, { Name = "${local.name}-db-subnet-group" })
}

resource "aws_db_parameter_group" "postgres16" {
  name   = "${local.name}-pg16"
  family = "postgres16"
  tags   = local.tags
}

resource "aws_db_instance" "this" {
  identifier = local.name

  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  allocated_storage     = var.allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [var.rds_sg_id]
  parameter_group_name   = aws_db_parameter_group.postgres16.name

  multi_az               = false   # single-AZ to save cost
  publicly_accessible    = false
  deletion_protection    = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "${local.name}-final-snapshot"
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  tags = local.tags
}
