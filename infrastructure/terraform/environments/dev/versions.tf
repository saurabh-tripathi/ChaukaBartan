terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # Uncomment once you have an S3 bucket for remote state:
  # backend "s3" {
  #   bucket         = "chaukabartan-tfstate"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-west-2"
  #   dynamodb_table = "chaukabartan-tflock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = var.project_name
      Application = "ChaukaBartan"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

provider "random" {}
