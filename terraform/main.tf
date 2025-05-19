resource "aws_db_instance" "postgres" {
  identifier          = "data-explorer-db"
  engine              = "postgres"
  engine_version      = "17.2"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  storage_type        = "gp2"
  username            = var.db_username
  password            = var.db_password
  publicly_accessible = true
  skip_final_snapshot = true
  apply_immediately   = true
}
