output "bucket_name" {
  value = aws_s3_bucket.lakehouse.bucket
}

output "glue_database_name" {
  value = aws_glue_catalog_database.riskflow.name
}
output "dynamodb_table_name" {
  value = aws_dynamodb_table.card_velocity.name
}