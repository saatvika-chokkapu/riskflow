resource "aws_s3_bucket" "lakehouse" {
  bucket = "riskflow-lakehouse-${random_id.suffix.hex}"
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id
  versioning_configuration {
    status = "Enabled"
  }
}