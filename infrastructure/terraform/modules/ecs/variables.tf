variable "project_name" { type = string }
variable "environment"  { type = string }
variable "region"       { type = string }
variable "app_image"    { type = string }

variable "cpu" {
  type    = number
  default = 256
}

variable "memory" {
  type    = number
  default = 512
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "app_port" {
  type    = number
  default = 8000
}

variable "subnet_ids"       { type = list(string) }
variable "ecs_sg_id"        { type = string }
variable "target_group_arn" { type = string }

variable "database_url_secret_arn" { type = string }
variable "secret_key_arn"          { type = string }
variable "ecr_repository_arn"      { type = string }
