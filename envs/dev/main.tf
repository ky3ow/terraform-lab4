provider "aws" {
  region = "eu-central-1"

  default_tags {
    tags = {
      ManagedBy = "Terraform"
      lab       = "4"
    }
  }
}

locals {
  prefix = "havryliuk-volodymyr-02"
}

module "database" {
  source     = "../../modules/dynamodb"
  table_name = "${local.prefix}-table"
}

module "logs_bucket" {
  source = "../../modules/bucket"
  name   = "${local.prefix}-logs-bucket"
}

module "backend" {
  source              = "../../modules/lambda"
  function_name       = "${local.prefix}-api-handler"
  source_file         = "${path.root}/../../src/app.py"
  dynamodb_table_arn  = module.database.table_arn
  dynamodb_table_name = module.database.table_name
  logs_bucket_arn     = module.logs_bucket.arn
  logs_bucket_name    = module.logs_bucket.name
}

module "api" {
  source               = "../../modules/api_gateway"
  api_name             = "${local.prefix}-http-api"
  lambda_invoke_arn    = module.backend.invoke_arn
  lambda_function_name = module.backend.function_name
}

output "api_url" {
  value = module.api.api_endpoint
}
