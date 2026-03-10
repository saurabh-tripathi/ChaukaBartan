variable "project_name" { type = string }
variable "environment"  { type = string }
variable "vpc_id"       { type = string }
variable "subnet_ids"   { type = list(string) }
variable "alb_sg_id"    { type = string }

variable "app_port" {
  type    = number
  default = 8000
}

variable "health_check_path" {
  type    = string
  default = "/health"
}

variable "domain_name" {
  type        = string
  description = "Primary domain (e.g. chaukabartan.com). Leave empty to skip HTTPS — add when you have a domain."
  default     = ""
}

variable "hosted_zone_id" {
  type        = string
  description = "Route 53 hosted zone ID for ACM DNS validation. Required when domain_name is set."
  default     = ""
}
