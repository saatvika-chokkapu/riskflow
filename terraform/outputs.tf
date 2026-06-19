output "bucket_name" {
  value = aws_s3_bucket.lakehouse.bucket
}

output "glue_database_name" {
  value = aws_glue_catalog_database.riskflow.name
}