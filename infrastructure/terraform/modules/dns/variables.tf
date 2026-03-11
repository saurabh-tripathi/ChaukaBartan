variable "project_name" { type = string }
variable "environment"  { type = string }

variable "root_domain" {
  type        = string
  description = "Root domain managed in this hosted zone (e.g. gradnuclei.com)."
}
