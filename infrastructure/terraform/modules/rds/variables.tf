variable "project_name" { type = string }
variable "environment"  { type = string }
variable "subnet_ids"   { type = list(string) }
variable "rds_sg_id"    { type = string }
variable "db_name"      { type = string }
variable "db_username"  { type = string }

variable "db_password" {
  type      = string
  sensitive = true
}

variable "instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "engine_version" {
  type    = string
  default = "16"
}

variable "allocated_storage" {
  type    = number
  default = 20
}
