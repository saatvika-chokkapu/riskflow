resource "aws_dynamodb_table" "card_velocity" {
  name         = "riskflow-card-velocity"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "card_id"

  attribute {
    name = "card_id"
    type = "S"
  }
}