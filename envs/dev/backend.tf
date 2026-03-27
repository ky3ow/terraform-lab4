terraform {
  required_version = ">= 1.10.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket  = "tf-state-lab4-havryliuk-volodymyr-02"
    key     = "envs/dev/terraform.tfstate"
    region  = "eu-central-1"
    encrypt = true
    use_lockfile = true
  }
}
