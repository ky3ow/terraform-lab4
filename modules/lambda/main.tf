variable "function_name" { type = string }
variable "source_file" { type = string }
variable "dynamodb_table_arn" { type = string }
variable "dynamodb_table_name" { type = string }
variable "logs_bucket_arn" { type = string }
variable "logs_bucket_name" { type = string }

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = var.source_file
  output_path = "${path.module}/app.zip"
}

resource "aws_iam_role" "lambda_exec" {
  name = "${var.function_name}_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "dynamodb_access" {
  name = "dynamodb_access_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["dynamodb:*"]
      Resource = var.dynamodb_table_arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "dynamodb_access" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

resource "aws_iam_policy" "bucket_access" {
  name = "bucket_access_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "${var.logs_bucket_arn}/logs/*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "bucket_access" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.bucket_access.arn
}

resource "aws_lambda_function" "api_handler" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = var.function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = "app.handler"
  runtime       = "python3.12"
  # Захист від зайвих деплоїв: оновлюється лише при зміні хешу файлу
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
      LOGS_BUCKET = var.logs_bucket_name
    }
  }
}

output "invoke_arn" {
  value = aws_lambda_function.api_handler.invoke_arn
}

output "function_name" {
  value = aws_lambda_function.api_handler.function_name
}
