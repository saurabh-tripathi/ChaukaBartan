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
  description = "Full ECR image URI. Leave empty on first apply; update after pushing the image."
  default     = ""
}

variable "domain_name" {
  type        = string
  description = "Primary domain for HTTPS (e.g. chaukabartan.com). Leave empty to use HTTP only."
  default     = ""
}

variable "hosted_zone_id" {
  type        = string
  description = "Route 53 hosted zone ID for ACM DNS validation. Required when domain_name is set."
  default     = ""
}
