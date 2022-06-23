#
# Terraform variable
#  * Provides aws_region environment variable for the deployment
#  * Provides cluster-name environment variable for the deployment
#
variable "aws_region" {
  default = "us-east-1"
}

variable "cluster-name" {
  default = "dashboards-anywhere-playground-prod"
  type    = string
}
