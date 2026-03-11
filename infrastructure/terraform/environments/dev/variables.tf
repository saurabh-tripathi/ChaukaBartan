variable "project_name" {
  type    = string
  default = "chaukabartan"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "region" {
  type    = string
  default = "us-west-2"
}

variable "db_name" {
  type    = string
  default = "chaukabartan"
}

variable "db_username" {
  type    = string
  default = "cbadmin"
}

variable "app_image" {
  type        = string
  description = "Backend ECR image URI. Leave empty on first apply; fill after pushing."
  default     = ""
}

variable "frontend_image" {
  type        = string
  description = "Frontend ECR image URI. Leave empty on first apply; fill after pushing."
  default     = ""
}

variable "root_domain" {
  type        = string
  description = "Root domain managed in Route 53 (e.g. gradnuclei.com)."
  default     = ""
}

variable "subdomain" {
  type        = string
  description = "Subdomain for this project (e.g. chaukabartan → chaukabartan.gradnuclei.com)."
  default     = "chaukabartan"
}

variable "app_password" {
  type        = string
  description = "Single-user login password for the web UI."
  sensitive   = true
}
